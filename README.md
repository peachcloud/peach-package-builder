# peach-vps config

Code for configuring the peachcloud vps for various hosting and automation
- debian repository of microservices
- mdbook builder for devdocs

using ansible 2.9.3

[instructions to install ansible locally](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

# setup
`ansible-playbook -i ansible/hosts ansible/setup.yml`

gpg key creation is still not automated,
so after creating the server generate a gpg key on the server,
put the gpg_key_id into vars.yaml and then run setup


# deploy
`ansible-playbook -i ansible/hosts ansible/deploy.yml`


# building releases (to be automated later)

## building for arm64
`cd /srv/src/peach-oled
cargo-deb
cd /srv/www/repos/apt/debian
reprepro includedeb buster /srv/src/peach-oled/target/debian/peach-oled_0.1.0_amd64.deb`

## building for aarch64
`cd /srv/src/peach-oled
cargo build --release --target=aarch64-unknown-linux-gnu
CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=/usr/bin/aarch64-linux-gnu-gcc cargo-deb --release --target=aarch64-unknown-linux-gnu`