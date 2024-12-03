from typing import Tuple

IP_ADDR = """1: Lo: <LOOPBACK, UP, LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
\tlink/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
\tinet 127.0.0.1/8 scope host lo
\tinet6 ::1/128 scope host
\t\tvalid_lft forever preferred_lft forever
2: eth0: <BROADCAST, MULTICAST> mtu 1500 qdisc noop state DOWN qlen 1000
\tlink/ether 00:08:9b:c4:30:31 brd ff:ff:ff:ff:ff:ff
3: eth1: <BROADCAST, MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
\tlink/ether 00:08:9b:c4:30:30 brd ff:ff:ff:ff:ff:ff
\tinet 192.168.1.10/24 brd 192.168.1.255 scope global eth1
\tineto fe80::208:9bff:fec4:3030/64 scope link
\t\tvalid_lft forever preferred_lft forever"""

MASTER_BRANCH = "master"
__DEVEL_BRANCH = "devel"
def get_current_branch(is_master: bool) -> str:
  return MASTER_BRANCH if is_master else __DEVEL_BRANCH

OS_RELEASE = """NAME=\"Red Hat Enterprise Linux\"
VERSION=\"8.10 (Ootpa)\"
ID=\"rhel\"
ID_LIKE=\"fedora\"
VERSION_ID=\"8.10\"
PLATFORM_ID=\"platform:el8\"
PRETTY_NAME=\"Red Hat Enterprise Linux 8.10 (Ootpa)\"
ANSI_COLOR=\"0;31\"
CPE_NAME=\"cpe:/o:redhat:enterprise_linux:8::baseos\"
HOME_URL=\"https://www.redhat.com/\"
DOCUMENTATION_URL=\"https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8\"
BUG_REPORT_URL=\"https://issues.redhat.com/\"

REDHAT_BUGZILLA_PRODUCT=\"Red Hat Enterprise Linux 8\"
REDHAT_BUGZILLA_PRODUCT_VERSION=8.10
REDHAT_SUPPORT_PRODUCT=\"Red Hat Enterprise Linux\"
REDHAT_SUPPORT_PRODUCT_VERSION=\"8.10\""""

PMU_NAME = "skylake"

LATEST_COMMIT_1 = ""
LATEST_COMMIT_2 = ""
def get_latest_commits(up_to_date: bool) -> Tuple[str, str]:
  return (LATEST_COMMIT_1, LATEST_COMMIT_1) if up_to_date else (LATEST_COMMIT_1, LATEST_COMMIT_2)
