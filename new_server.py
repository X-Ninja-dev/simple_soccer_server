import json
import asyncio
import websockets
import sys
import os
from pathlib import Path
import subprocess
import random


# DEBUG
comments = [
    "----------- WELCOME -----------",
    "This is where all the crazy action will be happening while the match is played!",
    "There will be highs and lows",
    "We will laugh and cry",
    "There might even be GOOOOOOOAAAAAALLLLLS",
    "But then again, it is football (soccer :-) ) so maybe not",
    "But should there be GOOOOOOOAAAAAALLLLLS, we will celebrate",
    "",
    "",
    "Nothing more here, because this part isn't actually implemented yet",
    "The match is being played on the server",
    "The score shown at the top are the actual score from the match",
    "All the comments are generated on the server too, but,",
    "The commentary are just the same for all matches",
    "",
    "Lets just end the match here",
    "Wait for it",
    "Waaaait for it",
    "Waaaaaait for it"
]


ai_teams = [
    {"players": [{ "name": "Buffon", "mp4_url": [], "image": [], "age": 21, "id": 21, "penalty": 61, "stamina": 61, "oneonone": 61, "aerial": 61, "passing": 61, "handling": 61, "command": 61, "positioning": 61, "reflexes": 61, "agility": 61, "energy": 100, "position": "GK", "rating": 61.0 }, { "name": "Roberto Carlos", "mp4_url": [], "image": [], "age": 21, "id": 22, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DML", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 }, { "name": "Cafu", "mp4_url": [], "image": [], "age": 21, "id": 23, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DMR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 }, { "name": "Maldini", "mp4_url": [], "image": [], "age": 21, "id": 24, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DCL", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 }, { "name": "Canavaro", "mp4_url": [], "image": [], "age": 21, "id": 25, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DC", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 }, { "name": "Pirlo", "mp4_url": [], "image": [], "age": 21, "id": 26, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DCR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 }, { "name": "Zidane", "mp4_url": [], "image": [], "age": 21, "id": 27, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "MCL", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 }, { "name": "Ronaldinho", "mp4_url": [], "image": [], "age": 21, "id": 28, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "MCR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 }, { "name": "Cristiano Ronaldo", "mp4_url": [], "image": [], "age": 21, "id": 29, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "AMCL", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 }, { "name": "Messi", "mp4_url": [], "image": [], "age": 21, "id": 30, "finishing": 61, "longshot": 61, "speed": 61, "crossing": 61, "passing": 61, "technique": 71, "tackle": 61, "positioning": 61, "stamina": 61, "heading": 61, "team": "", "position": "AMCR", "energy": 100, "corner": 61.00000000000001, "freekick": 61.0, "penalty": 61.00000000000001, "rating": 61.0 }, { "name": "Ronaldo", "mp4_url": [], "image": [], "age": 21, "id": 31, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "position": "FCR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0 } ], "settings": { "name": "All Stars AI", "mentality": "Normal", "strategy": "Balanced", "rating": 61 } },
    {"players": [{"name": "Preud'Homme", "mp4_url": [], "image": [], "age": 21, "id": 1, "penalty": 62, "stamina": 62, "oneonone": 62, "aerial": 62, "passing": 62, "handling": 62, "command": 62, "positioning": 62, "reflexes": 62, "agility": 62, "energy": 100, "position": "GK", "rating": 62.0}, {"name": "Grimaldo", "mp4_url": [], "image": [], "age": 21, "id": 2, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DML", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Cancelo", "mp4_url": [], "image": [], "age": 21, "id": 3, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DMR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Luis\u00e3o", "mp4_url": [], "image": [], "age": 21, "id": 4, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DCL", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Ruben Dias", "mp4_url": [], "image": [], "age": 21, "id": 5, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DC", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Florentino", "mp4_url": [], "image": [], "age": 21, "id": 6, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "DCR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Rui Costa", "mp4_url": [], "image": [], "age": 21, "id": 7, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "MCL", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Aimar", "mp4_url": [], "image": [], "age": 21, "id": 8, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "MCR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Di Maria", "mp4_url": [], "image": [], "age": 21, "id": 9, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "AMCL", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Rafa", "mp4_url": [], "image": [], "age": 21, "id": 10, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "AMCR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}, {"name": "Cardozo", "mp4_url": [], "image": [], "age": 21, "id": 11, "finishing": 62, "longshot": 62, "speed": 62, "crossing": 62, "passing": 62, "technique": 62, "tackle": 62, "positioning": 62, "stamina": 62, "heading": 62, "team": "", "position": "FCR", "energy": 100, "corner": 62.0, "freekick": 62.0, "penalty": 62.0, "rating": 62.0}], "settings": {"name": "Benfica AI", "mentality": "Normal", "strategy": "Balanced", "rating": 62}},
    {"players": [{"age": 18, "crossing": 40, "finishing": 48, "heading": 41, "id": 1280, "image": [], "is_copy": True, "longShot": 40, "mp4_url": ["", "C:/Users/schul/Downloads/legend/1280/background.mp4"], "name": "Daniel Black", "passing": 65, "placement": 4, "position": "FCL", "positioning": 40, "rating": 57, "speed": 40, "stamina": 59, "tackle": 40, "technique": 63}, {"age": 21, "crossing": 60, "finishing": 61, "heading": 68, "id": 5, "image": ["https://nftapi.nft11.io/6s62AQ9GZJGm3sTPQCWaGV.png", "C:/Users/schul/Downloads/legend/5/image.png"], "is_copy": True, "longShot": 54, "mp4_url": ["https://nftapi.nft11.io/g9wePFBFbk3pwB5hDhfgPb.mp4", "C:/Users/schul/Downloads/legend/5/background.mp4"], "name": "Daniel Wright", "passing": 66, "placement": 3, "position": "FC", "positioning": 70, "rating": 72, "speed": 50, "stamina": 72, "tackle": 61, "technique": 58}, {"age": 19, "crossing": 42, "finishing": 70, "heading": 48, "id": 905, "image": ["https://nftapi.nft11.io/6JxPuxeWsvR8x9kBoE6QC9.png", "C:/Users/schul/Downloads/legend/905/image.png"], "is_copy": True, "longShot": 55, "mp4_url": ["", "C:/Users/schul/Downloads/legend/905/background.mp4"], "name": "Brandon Madden", "passing": 41, "placement": 2, "position": "AML", "positioning": 46, "rating": 58, "speed": 51, "stamina": 41, "tackle": 41, "technique": 51}, {"age": 21, "crossing": 53, "finishing": 72, "heading": 63, "id": 1123, "image": ["https://nftapi.nft11.io/pqWRdV37nLGBWigg5Yrd97.png", "C:/Users/schul/Downloads/legend/1123/image.png"], "is_copy": True, "longShot": 69, "mp4_url": ["https://nftapi.nft11.io/oFPo2Pnyg5vK77BHr1c9vJ.mp4", "C:/Users/schul/Downloads/legend/1123/background.mp4"], "name": "Daniel Clemens", "passing": 61, "placement": 1, "position": "AMC", "positioning": 69, "rating": 73, "speed": 61, "stamina": 70, "tackle": 51, "technique": 61}, {"age": 21, "crossing": 78, "finishing": 65, "heading": 61, "id": 675, "image": ["https://nftapi.nft11.io/rYBFtPCwCveBRrbVDkwuh4.png", "C:/Users/schul/Downloads/legend/675/image.png"], "is_copy": True, "longShot": 53, "mp4_url": ["https://nftapi.nft11.io/oXM1pU1qDSyXCPW9NQ9Pua.mp4", "C:/Users/schul/Downloads/legend/675/background.mp4"], "name": "David Mullen", "passing": 59, "placement": 1, "position": "MC", "positioning": 61, "rating": 72, "speed": 63, "stamina": 65, "tackle": 58, "technique": 57}, {"age": 21, "crossing": 56, "finishing": 61, "heading": 73, "id": 703, "image": ["https://nftapi.nft11.io/qeUk78QFTDMnzr2MHqRrtx.png", "C:/Users/schul/Downloads/legend/703/image.png"], "is_copy": True, "longShot": 67, "mp4_url": ["https://nftapi.nft11.io/snfU7tsrCL4Z5pLYMGmHF8.mp4", "C:/Users/schul/Downloads/legend/703/background.mp4"], "name": "Jack Goodman", "passing": 59, "placement": 1, "position": "MR", "positioning": 55, "rating": 72, "speed": 54, "stamina": 79, "tackle": 57, "technique": 59}, {"age": 21, "crossing": 52, "finishing": 64, "heading": 58, "id": 1314, "image": ["https://nftapi.nft11.io/qaYC44ckLdZ9VrKNpFuhGV.png", "C:/Users/schul/Downloads/legend/1314/image.png"], "is_copy": True, "longShot": 69, "mp4_url": ["https://nftapi.nft11.io/bKbfeHfKWufDRhVkiNw1rY.mp4", "C:/Users/schul/Downloads/legend/1314/background.mp4"], "name": "Jayden Parsons", "passing": 59, "placement": 1, "position": "DML", "positioning": 70, "rating": 72, "speed": 54, "stamina": 57, "tackle": 76, "technique": 61}, {"age": 20, "crossing": 48, "finishing": 41, "heading": 50, "id": 184, "image": ["https://nftapi.nft11.io/hkVWGCBwHYrDMGLuPYRzDE.png", "C:/Users/schul/Downloads/legend/184/image.png"], "is_copy": True, "longShot": 41, "mp4_url": ["https://nftapi.nft11.io/kuoqtUXdNvHmHctW5EzhCN.mp4", "C:/Users/schul/Downloads/legend/184/background.mp4"], "name": "Brian Rowe", "passing": 58, "placement": 1, "position": "DMC", "positioning": 40, "rating": 58, "speed": 57, "stamina": 50, "tackle": 42, "technique": 55}, {"age": 21, "crossing": 56, "finishing": 62, "heading": 67, "id": 418, "image": ["https://nftapi.nft11.io/gaiFKP8Au1piiFUcez5LSL.png", "C:/Users/schul/Downloads/legend/418/image.png"], "is_copy": True, "longShot": 54, "mp4_url": ["https://nftapi.nft11.io/uhPx7Lf4RFXo6Q7MYeSN47.mp4", "C:/Users/schul/Downloads/legend/418/background.mp4"], "name": "Dylan Coffey", "passing": 67, "placement": 0, "position": "DC", "positioning": 62, "rating": 72, "speed": 53, "stamina": 66, "tackle": 62, "technique": 71}, {"age": 21, "crossing": 53, "finishing": 77, "heading": 68, "id": 1302, "image": ["https://nftapi.nft11.io/nbLgMQkmBAhviFve97DsNA.png", "C:/Users/schul/Downloads/legend/1302/image.png"], "is_copy": True, "longShot": 69, "mp4_url": ["https://nftapi.nft11.io/mg2uXJSPmzsTxwcYyysFcJ.mp4", "C:/Users/schul/Downloads/legend/1302/background.mp4"], "name": "Dylan Coffey", "passing": 57, "placement": 0, "position": "DCR", "positioning": 58, "rating": 72, "speed": 54, "stamina": 63, "tackle": 59, "technique": 62}, {"aerial": 61, "age": 21, "agility": 61, "command": 61, "energy": 100, "handling": 61, "id": 21, "image": [], "mp4_url": [], "name": "Buffon", "oneonone": 61, "passing": 61, "penalty": 61, "position": "GK", "positioning": 61, "rating": 61, "reflexes": 61, "stamina": 61, "team": ""}], "settings": {"mentality": "Normal", "name": "Atletico Madrid AI", "strategy": "Balanced", "rating": 67}},
    {"players": [{"age": 21, "crossing": 77, "finishing": 67, "heading": 62, "id": 1026, "image": [], "is_copy": True, "longShot": 61, "mp4_url": ["https://nftapi.nft11.io/twhdDUancp6EkdMBYUgzCT.mp4", "C:/Users/schul/Downloads/legend/1026/background.mp4"], "name": "Tyler Greene", "passing": 63, "placement": 3, "position": "FCL", "positioning": 54, "rating": 72, "speed": 70, "stamina": 54, "tackle": 56, "technique": 56}, {"age": 21, "crossing": 75, "finishing": 68, "heading": 65, "id": 56, "image": ["https://nftapi.nft11.io/9VXoenFwbyqp3v9bPNByHB.png", "C:/Users/schul/Downloads/legend/56/image.png"], "is_copy": True, "longShot": 60, "mp4_url": ["https://nftapi.nft11.io/ajDkJcJa7J8eVFyZSCaDSY.mp4", "C:/Users/schul/Downloads/legend/56/background.mp4"], "name": "Evan Whitney", "passing": 62, "placement": 3, "position": "FC", "positioning": 50, "rating": 72, "speed": 64, "stamina": 59, "tackle": 57, "technique": 60}, {"age": 21, "crossing": 50, "finishing": 59, "heading": 65, "id": 394, "image": ["https://nftapi.nft11.io/dSnUwBS2Ht2XmL5PW3SFio.png", "C:/Users/schul/Downloads/legend/394/image.png"], "is_copy": True, "longShot": 64, "mp4_url": ["https://nftapi.nft11.io/7STTjxKwyGSnyPWwrZYsLQ.mp4", "C:/Users/schul/Downloads/legend/394/background.mp4"], "name": "Joshua Hopkins", "passing": 80, "placement": 3, "position": "FCR", "positioning": 61, "rating": 72, "speed": 57, "stamina": 55, "tackle": 59, "technique": 70}, {"age": 21, "crossing": 60, "finishing": 50, "heading": 60, "id": 315, "image": ["https://nftapi.nft11.io/jQv47jz2CgVPAmF96eUMQ8.png", "C:/Users/schul/Downloads/legend/315/image.png"], "is_copy": True, "longShot": 61, "mp4_url": ["https://nftapi.nft11.io/rjyfPVSxekMfC4d9dnyFMN.mp4", "C:/Users/schul/Downloads/legend/315/background.mp4"], "name": "Miles Chen", "passing": 66, "placement": 2, "position": "AMCL", "positioning": 67, "rating": 72, "speed": 60, "stamina": 70, "tackle": 64, "technique": 62}, {"age": 21, "crossing": 52, "finishing": 75, "heading": 58, "id": 79, "image": ["https://nftapi.nft11.io/eqp3dSSHD5GbqZ2djTVrQM.png", "C:/Users/schul/Downloads/legend/79/image.png"], "is_copy": True, "longShot": 70, "mp4_url": ["https://nftapi.nft11.io/1HHamN1SBtncsogLKowqLs.mp4", "C:/Users/schul/Downloads/legend/79/background.mp4"], "name": "David Cooper", "passing": 64, "placement": 2, "position": "AMC", "positioning": 69, "rating": 72, "speed": 58, "stamina": 52, "tackle": 61, "technique": 61}, {"age": 20, "crossing": 56, "finishing": 50, "heading": 42, "id": 1062, "image": ["https://nftapi.nft11.io/pZfhtEJXRU4hCL8zKuBzwM.png", "C:/Users/schul/Downloads/legend/1062/image.png"], "is_copy": True, "longShot": 41, "mp4_url": ["", "C:/Users/schul/Downloads/legend/1062/background.mp4"], "name": "Andrew Dixon", "passing": 40, "placement": 2, "position": "AMCR", "positioning": 44, "rating": 58, "speed": 53, "stamina": 52, "tackle": 54, "technique": 56}, {"age": 19, "crossing": 55, "finishing": 42, "heading": 40, "id": 886, "image": ["https://nftapi.nft11.io/pkNrraEUyuyMV6UXmCWpcw.png", "C:/Users/schul/Downloads/legend/886/image.png"], "is_copy": True, "longShot": 40, "mp4_url": ["", "C:/Users/schul/Downloads/legend/886/background.mp4"], "name": "Anthony Boone", "passing": 66, "placement": 2, "position": "MC", "positioning": 44, "rating": 57, "speed": 46, "stamina": 40, "tackle": 41, "technique": 65}, {"age": 21, "crossing": 70, "finishing": 60, "heading": 55, "id": 657, "image": ["https://nftapi.nft11.io/cBts8hp1ySsTsveS5tmsyE.png", "C:/Users/schul/Downloads/legend/657/image.png"], "is_copy": True, "longShot": 60, "mp4_url": ["https://nftapi.nft11.io/dZ1q3zxeFjgJbF57t6a2JK.mp4", "C:/Users/schul/Downloads/legend/657/background.mp4"], "name": "Mason Sparks", "passing": 70, "placement": 1, "position": "DML", "positioning": 66, "rating": 72, "speed": 55, "stamina": 59, "tackle": 66, "technique": 59}, {"age": 18, "crossing": 40, "finishing": 40, "heading": 40, "id": 216, "image": ["https://nftapi.nft11.io/fPEbtzeBTpARozkayd2RLG.png", "C:/Users/schul/Downloads/legend/216/image.png"], "is_copy": True, "longShot": 43, "mp4_url": ["https://nftapi.nft11.io/8dKaWTaAe3kMgnqJzDYYrL.mp4", "C:/Users/schul/Downloads/legend/216/background.mp4"], "name": "Benjamin Vaughn", "passing": 69, "placement": 1, "position": "DMR", "positioning": 40, "rating": 58, "speed": 55, "stamina": 42, "tackle": 45, "technique": 66}, {"age": 21, "crossing": 72, "finishing": 55, "heading": 68, "id": 341, "image": ["https://nftapi.nft11.io/6Dgy4j8AxQPnkF2fN3JiHJ.png", "C:/Users/schul/Downloads/legend/341/image.png"], "is_copy": True, "longShot": 53, "mp4_url": ["https://nftapi.nft11.io/rgGmyWPUL5wfFS1okgdgjv.mp4", "C:/Users/schul/Downloads/legend/341/background.mp4"], "name": "Ryan Peters", "passing": 68, "placement": 0, "position": "DC", "positioning": 60, "rating": 72, "speed": 72, "stamina": 58, "tackle": 57, "technique": 57}, {"aerial": 61, "age": 21, "agility": 61, "command": 61, "energy": 100, "handling": 61, "id": 21, "image": [], "mp4_url": [], "name": "Buffon", "oneonone": 61, "passing": 61, "penalty": 61, "position": "GK", "positioning": 61, "rating": 61, "reflexes": 61, "stamina": 61, "team": ""}], "settings": {"mentality": "Normal", "name": "FC Copenhagen AI", "strategy": "Balanced", "rating": 67}}
]

# used to generate client id's when clients connect
client_id = len(ai_teams)
# clients are enterred as KEY = websocket VALUE = id :int
clients = {}
# teams are entered as [client_id, team]
teams_waiting = []


# DEBUG
match_playing = False

async def handler(websocket):
    # New client connected
    if not websocket in clients:
        clients[websocket] = get_new_id()
        # TODO: handle in the 'teams_waiting_changed' function
        teams = []
        for t in teams_waiting:
            data = t[1]["settings"]
            data["id"] = t[0]
            teams.append(data)
        response = json.dumps({"error" : "OK", "team_waiting" : teams})

        await websocket.send(response)
        await players_online_changed()
    while True:
        # TODO: refactor ALL of the exception handling here and in the rest of the file
        try:
            message = await websocket.recv()
            # print(f"message: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("\n-----------------------------------------------------------------------------")
            print(f"Client {websocket}") # with ID: {clients[websocket]} disconnected")
            print("-----------------------------------------------------------------------------\n")
            client_id = clients[websocket]
            # try to remove players team
            print(" --------------------- deleting client ------------------------------")
            del clients[websocket]
            await remove_waiting_team(client_id)
            await players_online_changed()
            break
        try:
            response = await decode_message(message, websocket)
        except Exception as e:
            print(f"Exception in Handler decode_message(message, websocket): {e}")
        try:
            await websocket.send(response)
        except Exception as e:
            print(f"Exception in Handler websocket.send(response): {e}")


async def decode_message(message, ws) -> json:
    msg = json.loads(message)
    request = msg["request"]
    if request == "join_waiting_list":
            _client_id = clients[ws]
            # TODO: check msg content is valid
            teams_waiting.append([_client_id, msg["team"]])
            await waiting_list_changed()
    elif request == "play_against":
            # set client team
            away_team = {}
            home_team = {}
            away_id = clients[ws]
            home_id = msg["team_id"]
            away_ws = ws
            try:
                home_ws_index = list(clients.values())[home_id]
                home_ws = list(clients.keys())[home_ws_index]
            except IndexError:
                # If home is AI team
                home_ws = None

            away_index = -1
            home_index = -1
            for index, team in enumerate(teams_waiting):
                if away_id == team[1]["settings"]["id"]:
                    away_index = index
                elif home_id == team[0]:
                    home_index = index

            # Home should never be -1 because it should always be in the teaqms waiting list
            if home_index != -1:
                home_team = teams_waiting[home_index][1]
            if away_index == -1:
                teams_waiting.pop(home_index)
            else:
                away_team = teams_waiting[away_index][1]
                teams_waiting.pop(max(home_index, away_index))
                teams_waiting.pop(min(home_index, away_index))
            
            # If the away team was not found it is because the player didn't join waiting so we take the team from the msg
            if away_index == -1:
                away_team = msg["team"]
            await waiting_list_changed()
            
            # If home is AI team there will be no socket to send too
            socks = [home_ws] if home_ws else []
            socks.append(away_ws)
            for sock in socks:
                # TODO: wait for feedback from users that they are ready to play
                await sock.send(json.dumps({"error" : "OK", "ready_for_match" : [home_team["settings"]["name"], away_team["settings"]["name"]]}))
            await play_match(home_team, away_team, socks)
    return json.dumps({"error" : "OK"})


def get_new_id() -> int:
    global client_id
    client_id += 1
    return client_id


async def players_online_changed():
    clients_online = len(clients)
    if clients_online > 0:
        print(f"{clients_online} players online")
        response = json.dumps({"error" : "OK", "players_online" : clients_online})
        for client in clients:
            await client.send(response)
    else:
        print("No players online\n\n")


async def waiting_list_changed():
    teams = []
    for t in teams_waiting:
        data = t[1]["settings"]
        data["id"] = t[0]
        teams.append(data)
    response = json.dumps({"error" : "OK", "team_waiting" : teams})
    for sock in clients:
        await sock.send(response)


async def remove_waiting_team(team_id):
    print(f"\n\n\nremoving team for client id: {team_id}\n\n\n")
    for index, team in enumerate(teams_waiting):
        if team_id == team[0]:
            print(f"found team team id {team[0]}")
            teams_waiting.pop(index)
            await waiting_list_changed()


async def play_match(home, away, socks):
    # DEBUG: using team from ai_teams for debug
    away = ai_teams[0]

    match_number = len([f.path for f in os.scandir("./matches") if f.is_dir()]) + 1
    path = f"./matches/{match_number}"
    os.makedirs(path)
    with open(f"{path}/{home['settings']['name']}.json", "w") as f:
        json.dump(home, f)
    with open(f"{path}/{away['settings']['name']}.json", "w") as f:
        json.dump(away, f)
    
    subprocess.run([sys.executable, "game.py", "-path", f"./matches/{match_number}/"])    

    report = ""
    with open(f"{path}/report.json", "r") as f:
        report = json.load(f)
    
    print(report["Team A"]["Goals"])
    print(report["Team B"]["Goals"])

    for sock in socks:
        await sock.send(json.dumps(
            {"error" : "OK",
             "match_score" : {
                 "home" : report["Team A"]["Goals"],
                 "away" : report["Team B"]["Goals"]
                 }
            })
        )

    # generating some fake match updates
    await asyncio.sleep(2)

    # TODO: refactor. match_playing used to catch if a client closes the game while playing a match
    #       NOT sure it has any effect the way the main while loop is written now
    match_playing = True
    for comment in comments:
        if match_playing:
            for sock in socks:
                try:
                    await sock.send(json.dumps({"error" : "OK", "match_update" : comment}))
                except Exception as e:
                    # Do no think this is ever hit the way the exception handling is in the main while loop
                    print(f"Exception in comments being send to clients: {e}")
                    match_playing = False
                    return
            await asyncio.sleep(random.random() + 1)
        else:
            continue
    
    if match_playing:
        await asyncio.sleep(2)
        for sock in socks:
            await sock.send(json.dumps({"error" : "OK", "match_finished" : report}))


async def main():
    print("\n\n-----------------------------------------------------------------------------")
    print("Server running")
    print("-----------------------------------------------------------------------------\n\n")
    async with websockets.serve(handler, "", 3389):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    for i, t in enumerate(ai_teams):
        teams_waiting.append([i+1, t])
    asyncio.run(main())