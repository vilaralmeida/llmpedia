import sys, os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from langchain_community.callbacks import get_openai_callback
from tqdm import tqdm

sys.path.append(os.environ.get("PROJECT_PATH"))
os.chdir(os.environ.get("PROJECT_PATH"))

import utils.vector_store as vs
import utils.db as db


def main():
    vs.validate_openai_env()

    arxiv_codes = db.get_arxiv_id_list(db.db_params, "summary_notes")
    title_map = db.get_arxiv_title_dict(db.db_params)
    done_codes = db.get_arxiv_id_list(db.db_params, "bullet_list_summaries")
    arxiv_codes = list(set(arxiv_codes) - set(done_codes))
    arxiv_codes = sorted(arxiv_codes)[::-1]

    for arxiv_code in tqdm(arxiv_codes):
        paper_notes = db.get_extended_notes(arxiv_code, expected_tokens=500)
        paper_title = title_map[arxiv_code]

        ## Insert copywriter's summary into the database.
        bullet_list = vs.convert_notes_to_bullets(paper_title, paper_notes, model="gpt-4o")
        bullet_list = bullet_list.replace("\n\n", "\n")
        db.insert_bullet_list_summary(arxiv_code, bullet_list)

    print("Done!")


if __name__ == "__main__":
    main()
