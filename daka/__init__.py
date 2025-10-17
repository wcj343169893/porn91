import logging
import sys
import argparse
import asyncio
import json

from daka.sign import Daka

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
)
_LOG = logging.getLogger(__name__)

def load_config(file_path="config.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file '{file_path}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{file_path}'.")
        return {}

async def main():
    parser = argparse.ArgumentParser(description="打卡系统自动打卡")
    # 最多采集页码
    parser.add_argument("max_page", type=str, nargs="?", help="最大页码")
    parser.add_argument("upload_url", type=str, nargs="?", help="上传地址")
    # oss
    parser.add_argument("access_key_id", type=str, nargs="?", help="oss access_key_id")
    parser.add_argument("secret_access_key", type=str, nargs="?", help="oss secret_access_key")
    parser.add_argument("oss_bucket_name", type=str, nargs="?", help="oss bucket name")
    parser.add_argument("oss_user_id", type=str, nargs="?", help="oss user id")


    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", action="store_true", dest="verbose", help="详细模式，显示更多运行信息")
    group.add_argument("-q", action="store_true", dest="quiet", help="安静模式，不显示运行信息")
    args = parser.parse_args()

    # if args.verbose:
    #     logging.getLogger(__name__).setLevel(logging.DEBUG)
    #     logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)
    #     logging.debug("详细模式..")

    # if args.quiet:
    #     logging.getLogger().setLevel(logging.CRITICAL)
        
    # Load configuration from file
    config = load_config()

     # Use command-line arguments if provided, otherwise fallback to config
    max_page = args.max_page if args.max_page else config.get("MAX_PAGE", 5)
    upload_url = args.upload_url if args.upload_url else config.get("UPLOAD_URL")
    access_key_id = args.access_key_id if args.access_key_id else config.get("OSS_KEY_ID")
    secret_access_key = args.secret_access_key if args.secret_access_key else config.get("OSS_ACCESS_KEY")
    oss_bucket_name = args.oss_bucket_name if args.oss_bucket_name else config.get("OSS_BUCKET_NAME")
    oss_user_id = args.oss_user_id if args.oss_user_id else config.get("OSS_UID")

    if not all([upload_url, access_key_id, secret_access_key, oss_bucket_name, oss_user_id]):
        print("Error: Missing required parameters. Please provide them via command-line arguments or config.json.")
        sys.exit(1)

    try:
        _LOG.debug("Initializing Daka ")
        app = Daka(int(max_page), upload_url, access_key_id, secret_access_key, oss_bucket_name, oss_user_id)
        _LOG.debug("Daka initialized successfully.")
        await app.auto_sign()
    except KeyboardInterrupt:
        _LOG.info("退出..")
        sys.exit()
    except Exception as e:
        _LOG.error("An error occurred: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
