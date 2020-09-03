# dip-faucet

## server side

```
# get source code
cd <working_dir>
git clone https://github.com/Dipper-Labs/dip-faucet.git && cd dip-faucet

# start redis
redis-server &

# setup config.ini file

# start clfacet.py
python main.py 1>result.log 2>&1
input password of from account, main process will be in demon mode
```

## client side

```
# you can get 100 tokens each call and max 2000 tokens per day.
curl http://<your_server_ip>/get_token?<dip_address>
```
