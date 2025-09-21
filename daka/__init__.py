import logging
import sys
import argparse
import asyncio

from daka.sign import Daka

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
)
_LOG = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="打卡系统自动打卡")
    parser.add_argument("username", type=str, nargs="?", help="用户名")
    parser.add_argument("password", type=str, nargs="?", help="密码")
    # email
    parser.add_argument("email", type=str, nargs="?", help="163邮箱账号")
    parser.add_argument("email_password", type=str, nargs="?", help="163邮箱专用密码")
    parser.add_argument("to_email", type=str, nargs="?", help="接收打卡结果的邮箱")

    # 最多采集页码
    parser.add_argument("max_page", type=str, nargs="?", help="最大页码")


    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", action="store_true", dest="verbose", help="详细模式，显示更多运行信息")
    group.add_argument("-q", action="store_true", dest="quiet", help="安静模式，不显示运行信息")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger(__name__).setLevel(logging.DEBUG)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)
        logging.debug("详细模式..")

    if args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL)
    # username, password 必填
    if not args.username or not args.password:
        parser.print_help()
        sys.exit(1)

    try:
        _LOG.debug("Initializing Daka with username: %s", args.username)
        app = Daka(args.username, args.password, args.email, args.email_password,
                   args.to_email, int(args.max_page) if args.max_page else 5)
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
