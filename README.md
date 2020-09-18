#OLX Price Checker 

## General info
This project is price checker. Compare price of PC setup on OLX with allegro components price.  

You must have a allegro client id and secret key to use.

More info on: https://developer.allegro.pl/about/

## Setup
Install requirements

`pip3 install -r requirements.txt`

Show only profitable offers **(Warning! Most offers are not profitable)**, output in cli 

`python3 cli <allegro client id> <allegro client secret key> -np`

Show all offers, output in json file

`python3 cli <allegro client id> <allegro client secret key> -np --json`

###Run tests 
`test` 