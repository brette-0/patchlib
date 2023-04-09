Producer's Notice
#################
Hi there! My name is Brette and I am the Developer of this module and I have a little story to tell if you continue reading about how this project came to be.

I was originally given the task of an auto-patch Discord bot that would process these patches against a comapred ROM, for this I needed a basic understanding of how the ``ips`` filetype worked and I spent about a week consitently researching this.

After much time into the projects development I had got in contact witht he owner of the Super Mario Bros 3 Modding Discord and suggested that I make a bot which countered Piracy and if a ROM was present, it would create an ``ips`` file for it, while it has the drawbacks of essentially creating other games (assuming they are larger than Super Mario Bros 3) this is to be expected and appreciated as impossible for me to control.

The original ``ips`` contrusction code was incredibly crude, producing unoptimized large ``ips`` files and did not solve the early ``EOF`` issue in which the offset 4542278 was misinterpreted as the footer which serves to terminate patching. It took me about two weeks to create this bot another week spent on the ``ips`` construction code and another week spent misunderstanding the ``discord.py`` API.

After this I had learned much more Python, as of writing this I am yet to have reached adulthood and am a hobbyist developer who as of writing this can only code in Python and MOS 6502 Assembly. During this time period the AI Assistant ChatGPT was released to the public and I soon found a better teacher than I ever had, while it often suggested minor optimizaitons - the effortless nature in which I recieved answers for any queery I had made learning a fast and fun process which improved my worth ethic, mentality and undoubtly the product quality too.

After reviewing my code on both my Discord bots I had concluded that the code was simply inadequate, I am no perfectionist but if there is an identifiable problem then there is a conjurable solution. After at least a dozen attempts at creating optimized build code, countless tests on ``instance`` handling with all of it's unnecessarily helpful and complicated optional kwargs I had created the best ``ips`` handler the world has seen.

I have much to be greatful for, if it were not for the incredibly awkardly wrote ``ips`` filetype docs that I stumbled on when researching for file structure I would never have gotten to where I am. No one should go through the struggle that I did to get where I am, for this I create the best tool that I can and I offet detailed explanatory documentation on the filetype and the module such that no one should ever be confused about this again.

In it's current state, ``patchlib`` only supports ``ips``, however there are immediate plans to approach the different ``patch`` types with the same ideology and structure as ``patchlib.ips``. If you have found this tool helpul whatsoever and have read up until this part, please feel free to join the `Discord Server <https://www.discord.gg/3DYCru4dCV>`_ where you can see all of my products, including the aforementioned bots that use this module!