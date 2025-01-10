
from datetime import datetime


class CommonConfig:
    llm_model = "gpt-3.5"
    debug = False
    update_interval = 2
    local_char_storage_path = f"ckpts/{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}/characters"
    local_blg_storage_path = f"ckpts/{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}/buildings"
    load_from = f"ckpts/2024-03-21-02:05:13"