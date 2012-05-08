Shoreditch Gamerunner
=====================

This is the server runner for the Shoreditch AI competition. It should be used during development of competitors to test them and will be used to run the final competition.

AIs
---

To automatically register an AI with the gamerunner (especially useful during testing) you must reference the AI in `preload_ais.py`


Overview
---

An overview of the game can be seen on [the details page](https://siliconmilkroundabout.wazoku.com/details).

Entering the competition
---

It is easiest to build your entry based on the [SampleAI](https://github.com/Wazoku/Shoreditch-SampleAI). You can find instructions on how to do that in the SampleAI README.


Communication
---
If you want to write your entry without using the [SampleAI](https://github.com/Wazoku/Shoreditch-SampleAI), you're probably going to have to have a look at the code in the `handlers/` directory and `logic.py` to figure out exactly how stuff works, however it's also helpful to know the general flow and structure of a game.

All AIs must expose a number of standard HTTP urls, and the host much be registered with the gamerunner, either by using the interface at /ui/ or by adding the endpoint to `preload_ais.py`. Everything in the `/ui/` or `/admin/` directory is related to creating and viewing a game, and should not be accessed by an AI.

All communication uses JSON, and the Content-Type for requests should be "application/json". Every request from the server to an AI will include a `player` key, which contains the current state of the AI's player.

When a game starts, the Gamerunner POSTS to `/game/<game_id>/` passing the `player`'s own information and the `endpoint` of the server.  If there is a problem starting the game the Gamerunner will then POST to `/game/<game_id>/cancel`.

When a player's turn starts, a POST is sent to `/game/<game_id>/start_turn`. If the AI wishes to take it's turn, it should respond with status 200, and it wishes to skip it's turn respond with any other status. From the time the AI responds, it has 15 seconds to take it's turn before it is automatically timed out. If your AI runs out of time it will be informed with a POST to `/game/<game_id>/end_turn`.

Assuming the AI accepts it's turn, it can then perform the following actions:
* Purchase 1 PR by POSTING to `/game/<game_id>/purchase_pr`
* Purchase 1 generator by POSTING to `/game/<game_id>/purchase_generator`
* Upgrade 1 generator by POSTING to `/game/<game_id>/upgrade_generator`
* Request a trade by POSTING to `/game/<game_id>/trade`
* End its turn by POSTING to `/game/<game_id>/end_turn`

When the game is over, the server with send a DELETE request to `/game/<game_id>`.

The player object contains a `secret` which must be sent in the body of every request by the AI (under the key `secret`).

### Purchase PR
When purchasing PR, you must ensure you have enough resources to cover the cost. If you successfully purchase the PR the server will return status 200, otherwise it will return 400.

### Purchase Generator
When purchasing a generator, you must ensure you have enough resources to cover the cost, and no more than 4 basic generators. If you successfully purchase the generator the server will return status 200, with the type of the generator in the body as `generator_type`, otherwise it will return 400.

### Upgrade Generator
When upgrading a generator, you must ensure you have enough resources to cover the cost, no more than 4 improved generators, and at least one of the type of generator you wish to upgrade. The AI must POST with `generator_type` in body. If you successfully upgrade the generator the server will return status 200, with the type of the generator in the body as `generator_type`, otherwise it will return 400.

### Trading
To initiate a trade, the POST must contain a `offering` key in the body, which contains resource -> number of every resource being offered for trade, and a `requesting` key which contains resource -> number of every resource being requested. If the trade is accepted then the server will return with status 200, including an `accepted_by` key which will be either the ID of the player who accepted, or 'bank' if it was traded with the bank.

When a trade is offered to you, the server will POST to `/game/<game_id>/trade` with the body containing `player` which is the ID of the player requesting the trade, `offering` which contains resource -> number of every resource being offered, and `requesting` which contains resource -> number of every resource being requested. If you wish to accept the request, respond with status 200, otherwise respond with any other status code.

### Player

When a player is sent, it contains:

* secret, which is a code which must be sent with every instruction to verify identity
* generators, which is resource -> number for basic generators
* improved_generators, which is resource -> number for improved generators
* resources, which is resource -> number
* pr, which is the amount of PR the player has
* customers, which is the amount of customers the player has
* actions, which contains all of the actions taken by other players since this player's last turn
