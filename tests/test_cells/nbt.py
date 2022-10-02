# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # init

# %%
import csv
print("initialized")

# %% [markdown]
# # test: first thing
#

# %%
FILES_HASH_PERSON = b'MyApp Files Hash'
h = hashlib.blake2b(digest_size=32, person=FILES_HASH_PERSON)
h.update(b'the same content')
assert h.hexdigest() == '20d9cd024d4fb086aae819a1432dd2466de12947831b75c5a30cf2676095d3b4'
print("XXXXXXXXXXXXXXXXXX")


# %% [markdown]
# # init

# %%
import hashlib

# %% [markdown]
# # something else

# %%
raise TypeError

# %% [markdown]
# # test: second thing

# %%
FILES_HASH_PERSON = b'MyApp Files Hash'
h = hashlib.blake2b(digest_size=32, person=FILES_HASH_PERSON)
h.update(b'the same content')
assert h.hexdigest() != '20d9cd024d4fb086aae819a1432dd2466de12947831b75c5a30cf2676095d3b4'


# %%
raise ValueError
