import os
import sys
import time
import logging
import yaml
from typing import List, Tuple, Set
from models import Job
from filters import matches, is_priority
from dedup import load_seen, save_seen, partition_new
from notify import (chunk_messages, send_telegram, send_telegram_document,
                    format_job_with_ats)
from sources import greenhouse, lever, ashby, adzuna, remotive
from sources import smartrecruiters, remoteok, themuse, jobicy, arbeitnow, himalayas

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("qa-radar")
HERE = os.path.dirname(os.path.abspath(__file__))


def collect(cfg) -> List[Job]:
    jobs: List[Job] = []
    watchlist = cfg.get("watchlist", {}) or {}
    for c in watchlist.get("greenhouse", []) or []:
        jobs += greenhouse.fetch(c)
    for c in watchlist.get("lever", []) or []:
        jobs += lever.fetch(c)
    for c in watchlist.get("ashby", []) or []:
        jobs += ashby.fetch(c)
    for c in watchlist.get("smartrecruiters", []) or []:
        jobs += smartrecruiters.fetch(c)
    discovery = cfg.get("discovery", {}) or {}
    if discovery.get("enabled"):
        jobs += adzuna.fetch(os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY"),
                             discovery.get("queries", ["sdet"]))
        jobs += remotive.fetch(discovery.get("remotive_search", "qa"))
        if discovery.get("remoteok"):
            jobs += remoteok.fetch()
        if discovery.get("arbeitnow"):
            jobs += arbeitnow.fetch()
        if discovery.get("jobicy_tags"):
            jobs += jobicy.fetch(discovery.get("jobicy_tags"))
        if discovery.get("himalayas"):
            jobs += himalayas.fetch(discovery.get("himalayas_limit", 50))
        muse = discovery.get("themuse") or {}
        if muse.get("enabled"):
            jobs += themuse.fetch(muse.get("pages", 3),
                                  muse.get("categories"),
                                  muse.get("locations"))
    return jobs


def select_new(jobs: List[Job], cfg, seen: Set[str]) -> List[Tuple[Job, bool]]:
    fresh = partition_new([j for j in jobs if matches(j, cfg)], seen)
    return [(j, is_priority(j, cfg)) for j in fresh]


def process_with_resume(selected: List[Tuple[Job, bool]], cfg, token, chat, dry):
    """Process each job: fetch JD → check experience → optimize resume → send."""
    from ats.jd_fetcher import fetch_job_description
    from ats.jd_parser import experience_matches
    from ats.keyword_extractor import extract_keywords, get_resume_keywords
    from ats.scorer import calculate_ats_score
    from ats.optimizer import optimize_resume
    from ats.pdf_generator import generate_pdf

    resume_cfg = cfg.get("resume", {})
    my_years = resume_cfg.get("experience_years", 3)
    max_target = resume_cfg.get("max_target_years", 6)
    max_resumes = resume_cfg.get("max_resumes_per_run", 10)

    # Load base resume
    resume_path = os.path.join(HERE, "resume", "base.yaml")
    with open(resume_path) as f:
        base_resume = yaml.safe_load(f)

    pdf_dir = os.path.join(HERE, "state", "resumes")
    os.makedirs(pdf_dir, exist_ok=True)

    resumes_generated = 0

    for job, priority in selected:
        # Fetch full job description
        jd_text = fetch_job_description(job)

        # Check experience match
        exp_ok, exp_info = experience_matches(jd_text or "", my_years, max_target)

        if exp_ok and resumes_generated < max_resumes:
            # Extract JD keywords
            jd_keywords = extract_keywords(jd_text or "")

            # Optimize resume (inject ALL JD keywords)
            optimized = optimize_resume(base_resume, jd_keywords, job.title)

            # Get keywords now present in optimized resume
            resume_keywords = get_resume_keywords(optimized)

            # Calculate ATS score
            ats_result = calculate_ats_score(
                resume_keywords, jd_keywords, job.title, optimized.get("summary", ""))

            # Generate PDF
            safe_name = f"{job.company}_{job.title}".replace(" ", "_")[:40]
            pdf_path = os.path.join(pdf_dir, f"AnubhavKaushik_{safe_name}.pdf")
            pdf_ok = generate_pdf(optimized, pdf_path)

            # Format message
            caption = format_job_with_ats(job, priority, exp_info, ats_result)

            if dry:
                score_marker = "\u2705" if ats_result["score"] >= 90 else "\u26A0\uFE0F"
                print(f"{score_marker} ATS:{ats_result['score']}% | {caption}")
                if ats_result.get("missing"):
                    print(f"   Gap: {', '.join(ats_result['missing'][:5])}")
                print(f"   PDF: {'generated' if pdf_ok else 'FAILED'}")
                print("---")
            else:
                if pdf_ok:
                    send_telegram_document(token, chat, pdf_path, caption)
                else:
                    send_telegram(token, chat, caption)
                time.sleep(1.5)

            resumes_generated += 1
        else:
            # Experience doesn't match OR resume limit reached — send job alert only
            if not exp_ok:
                caption = format_job_with_ats(job, priority, exp_info, None)
                caption += "\n\U0001F4CB No tailored resume — apply if role interests you"
            else:
                caption = format_job_with_ats(job, priority, exp_info, None)
                caption += "\n\U0001F4CB Resume limit reached for this run"

            if dry:
                print(f"\u2139\uFE0F  {caption}")
                print("---")
            else:
                send_telegram(token, chat, caption)
                time.sleep(1)


def main():
    dry = "--dry-run" in sys.argv
    seed = "--seed" in sys.argv
    with open(os.path.join(HERE, "config.yaml")) as f:
        cfg = yaml.safe_load(f)
    seen_path = os.path.join(HERE, "state", "seen.json")
    seen = load_seen(seen_path)
    jobs = collect(cfg)
    log.info("collected %d raw jobs", len(jobs))
    selected = select_new(jobs, cfg, seen)
    log.info("%d new matching jobs", len(selected))

    if seed:
        for j, _ in selected:
            seen.add(j.id)
        save_seen(seen_path, seen)
        log.info("seeded %d jobs as seen (no alerts sent)", len(selected))
        return

    if not selected:
        return

    token, chat = os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")

    # Use resume pipeline if resume config is present
    resume_cfg = cfg.get("resume", {})
    if resume_cfg.get("enabled", False):
        process_with_resume(selected, cfg, token, chat, dry)
    else:
        # Fallback: simple alerts without resume
        messages = chunk_messages(selected)
        if dry:
            for m in messages:
                print(m)
                print("\n---\n")
        else:
            header = f"\U0001F6A8 {len(selected)} new SDET/Automation job(s):"
            send_telegram(token, chat, header)
            for m in messages:
                time.sleep(1)
                send_telegram(token, chat, m)

    # Mark as seen
    if not dry:
        for j, _ in selected:
            seen.add(j.id)
        save_seen(seen_path, seen)


if __name__ == "__main__":
    main()
