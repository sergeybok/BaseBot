#!/bin/bash

mkdir templates
cd templates
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/templates/index.html" > index.html
chmod +x index.html
cd ../

mkdir static
cd static 
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/static/styles.css" > styles.css
chmod +x styles.css
cd ../
