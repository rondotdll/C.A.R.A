# C.A.R.A
GPT powered dynamic discord bot

## To the person reviewing this project
This whole thing was hacked together fairly quickly during what I like to call 
the "GPT surge", shortly after [not-so] OpenAI released GPT3.5 and the API to 
go along with it (Late ~2022ish).

**There are a number of different things that can (should absolutely) be improved**, 
but this project ended up getting abandoned due to time constraints.

### For example:
1. GPT3.5 is now considered a legacy product (crazy, right?) and the API has been
effectively re-written to fit it's [3] predecessors.
2. The list of garbage characters found in `cara/flexmatch/cmap.py` should be 
converted to a more lightweight and more readable format, to be loaded at
runtime.
3. There are a number of hardcoded values that could be moved to a config file.
4. There are a large number of essential moderation features that have yet to be 
implemented.