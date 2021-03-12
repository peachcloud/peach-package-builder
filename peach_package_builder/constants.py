# constants used by build and setup scripts
import os

# path to project directory
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# before running this script run `gpg --gen-key` on the server
# assign the email address of the key id here:
GPG_KEY_EMAIL = "andrew@mycelial.technology"
GPG_KEY_PASS_FILE = "/home/rust/passphrase.txt"

AUTOMATION_DIR = "/srv/peachcloud/automation"
FREIGHT_CONF = "/etc/freight.conf"
FREIGHT_LIB = "/var/lib/freight"
FREIGHT_CACHE = "/var/www/apt.peachcloud.org"
MICROSERVICES_SRC_DIR = "/srv/peachcloud/automation/microservices"
MICROSERVICES_DEB_DIR = "/srv/peachcloud/debs"
USER_PATH = "/home/rust"
CARGO_PATH = os.path.join(USER_PATH, ".cargo/bin/cargo")

SERVICES = [
    {"name": "peach-buttons",
     "repo_url": "https://github.com/peachcloud/peach-buttons.git"},
    {"name": "peach-menu", "repo_url": "https://github.com/peachcloud/peach-menu.git"},
    {"name": "peach-monitor",
     "repo_url": "https://github.com/peachcloud/peach-monitor.git"},
    {"name": "peach-network",
     "repo_url": "https://github.com/peachcloud/peach-network.git"},
    {"name": "peach-oled", "repo_url": "https://github.com/peachcloud/peach-oled.git"},
    {"name": "peach-stats", "repo_url": "https://github.com/peachcloud/peach-stats.git"},
    {"name": "peach-probe", "repo_url": "https://github.com/peachcloud/peach-probe.git"},
    # {"name": "peach-web", "repo_url": "https://github.com/peachcloud/peach-web.git"}, # currently build fails because it needs rust nightly for pear
]