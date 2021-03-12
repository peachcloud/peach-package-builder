#rsync -avzh --delete -e "ssh -i /Users/maxfowler/.ssh/peach_rsa" . notplants@167.99.136.8:/srv/peachcloud/automation/peach-vps
KEY_FILE=/Users/notplants/.ssh/peach_rsa
rsync -avzh --exclude target --exclude .idea --exclude .git --delete -e "ssh -i $KEY_FILE" . notplants@167.99.136.83:/srv/peachcloud/automation/peach-package-builder/
#ssh -i ./secret_files/do_rsa root@159.89.5.141
#ssh -i /home/notplants/.ssh/peach_rsa rust@167.99.136.83 'cd /srv/peachcloud/automation/peach-vps/; python3 scripts/build_packages.py'
#echo "cd /srv/src/peach-vps; python3 scripts/setup_vps.py"