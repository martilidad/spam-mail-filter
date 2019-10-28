find . -name '*.py' -print0 | xargs -0 yapf -i
read -p "Autoformat Complete. Press [Enter] key."
