#!/usr/bin/env bash
ansible-playbook -i ansible/hosts ansible/setup.yml
ansible-playbook -i ansible/hosts ansible/deploy.yml
