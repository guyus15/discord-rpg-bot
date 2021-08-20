import discord
import asyncio
import os
import sys

from discord.ext import commands
from discord.ext.commands.core import command

from rpg_player import Player
from rpg_item import Item
from rpg_json_handler import JsonHandler
from rpg_crafting import CraftingSystem
from rpg_bot_info import BotInfo

discord_token = ""

try:
    if not "RPG_BOT" in os.environ:
        raise KeyError

    discord_token = os.environ['RPG_BOT']

except KeyError:
    print("ERROR: Could not find environment variable 'RPG_BOT'")
    sys.exit(1)

users_file = "rpg_users.json"

PREFIX = "r"

bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True, help_command=None)

@bot.event
async def on_ready():
    crafting_system = CraftingSystem()
    BotInfo.set_crafting_system(crafting_system)

    print('Logged on as {0}!'.format(bot.user))

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your every move."))


@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return

    ctx.content = ctx.content.lower()

    BotInfo.set_last_message(ctx)

    await find_player(ctx)

    await bot.process_commands(ctx)


@bot.event
async def on_command_error(ctx, error):
    player_found = await find_player(ctx)

    print(error)

    if isinstance(error, commands.CommandNotFound):

        if player_found:
            embed_var = discord.Embed(title="Information",
                                      description="Could not find this command. Try using `{}help`".format(PREFIX),
                                      color=ctx.author.color)
        else:
            embed_var = discord.Embed(title="Information",
                                      description="It looks like you are new. Use `{}start` to begin the RPG".format(
                                          PREFIX), color=ctx.author.color)

        embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed_var)


async def find_player(ctx):
    for user in JsonHandler.get_users():
        if user["name"] == str(ctx.author):
            player = Player(str(ctx.author), user)
            BotInfo.set_current_player(player)

            return True

    return False


async def get_player(ctx, player_name):

    player = None

    for user in JsonHandler.get_users():
        if user["name"] == player_name:
            player = Player(ctx.author, user=user)

    if not player is None:
        print("I have found player {}!".format(player.name))
    else:
        print("I have not found any player's with this name")


async def create_player(ctx):
    player_found = await find_player(ctx)

    if not player_found:
        new_player = Player(ctx.author)

        with open(users_file, "r") as file:
            file_string = str(file.read())

        with open(users_file, "w+") as file:
            file_string = file_string.replace("\n", "")[:-2]

            file_string += ", " + new_player.player_to_json() + "]}"

            file.write(str(file_string))

        embed_var = discord.Embed(title="Information",
                                  description="**Welcome to RPGBot {}.**\n"
                                              "For help use '{}help' ro list all commands."
                                  .format(ctx.author.mention, PREFIX), color=ctx.author.colour)
    else:
        embed_var = discord.Embed(title="Information",
                                  description="**You already have an account, {}**".format(ctx.author.mention),
                                  color=ctx.author.colour)

    embed_var = embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)


async def split_into_pages(item_list, per_page):
    final_list = []
    item_count = 0

    if isinstance(item_list, dict):

        current_dict = {}

        for index, item in enumerate(item_list):

            if item_count < per_page:
                current_dict[item] = item_list.get(item)
                item_count += 1
            else:
                final_list.append(current_dict)
                item_count = 0
                current_dict = {item: item_list.get(item)}
                item_count += 1

            if index == len(item_list) - 1:
                final_list.append(current_dict)

    elif isinstance(item_list, list):

        current_list = []

        for index, item in enumerate(item_list):

            if item_count < per_page:
                current_list.append(item)
                item_count += 1
            else:
                final_list.append(current_list)
                item_count = 0
                current_list = [item]
                item_count += 1

            if index == len(item_list) - 1:
                final_list.append(current_list)

    return final_list


@bot.command(hidden=True)
async def start(ctx):
    await create_player(ctx)


@bot.command(hidden=True)
async def help(ctx, command_name=None):

    start_commands = list(bot.commands)
    all_commands = []

    for command in start_commands:
        # Hide all commands with the hidden parameter
        if command.hidden:
            continue

        all_commands.append(command)

    if not command_name is None:

        found_command = None

        for command in all_commands:

            if command.name == command_name or command_name in command.aliases:
                found_command = command

        if found_command is None:
            embed_var = discord.Embed(title="Help",
                                    description="**{} Could not find command with name** `{}`\nType `{}help` to view all commands".format(ctx.author.mention, command_name, PREFIX),
                                    color=ctx.author.colour)
            embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed_var)
            return

        embed_var = discord.Embed(title="Help",
                                  description="{} Showing details about the `{}` command:".format(ctx.author.mention, command_name),
                                  color=ctx.author.colour)

        embed_var.add_field(name="Command name: {}".format(found_command.name), value="{}".format(found_command.help), inline=False)
        embed_var.add_field(name="Usage: ", value="`{}`".format(found_command.usage), inline=True)

        embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed_var)
        return  

    cur_page = 0

    embed_var = discord.Embed(title="Help",
                              description="Showing all commands for {}".format(ctx.author.mention),
                              color=ctx.author.colour)

    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)


    pages_list = await split_into_pages(list(all_commands), 5)

    if len(pages_list) > 1:
        embed_var.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

    def populate_page(embed):
        for command in pages_list[cur_page]:
            embed.add_field(name="`{}`".format(command.name),
                                value="**{}**\nUsage: `{}`".format(command.brief, command.usage),
                                inline=False)

    populate_page(embed_var)

    message = await ctx.send(embed = embed_var)

    if len(pages_list) > 1:
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)
                # waiting for a reaction to be added - times out after x seconds, 60 in this
                # example

                if str(reaction.emoji) == "▶️":

                    cur_page += 1

                    if cur_page > len(pages_list) - 1:
                        cur_page = 0
        
                    new_embed = discord.Embed(title="Help",
                                description="Showing all commands for {}".format(ctx.author.mention),
                                color=ctx.author.colour)
                    
                    new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                    populate_page(new_embed)

                    new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                    await message.edit(embed=new_embed)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️":

                    cur_page -= 1

                    if cur_page < 0:
                        cur_page = len(pages_list) - 1

                    new_embed = discord.Embed(title="Help",
                                description="Showing all commands for {}".format(ctx.author.mention),
                                color=ctx.author.colour)
                    
                    new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                    populate_page(new_embed)

                    new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                    await message.edit(embed=new_embed)
                    await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await message.delete()
                break
                # ending the loop if user doesn't react after x seconds


@bot.command(help="Chop a tree and gather wood.\nCan only be used if you have an axe",
            brief="Chop and get wood",
            usage="{}chop".format(PREFIX),
            aliases=["c"])
async def chop(ctx):
    embed_var = discord.Embed(title="Chopping", description=BotInfo.current_player.chop(), color=ctx.author.colour)
    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)


@bot.command(help="Explore a mine and gather resources.\nCan only be used if you have a pickaxe",
            brief="Mine and get resources",
            usage="{}mine".format(PREFIX),
            aliases=["m"])
async def mine(ctx):
    embed_var = discord.Embed(title="Mining", description=BotInfo.current_player.mine(), color=ctx.author.colour)
    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)


@bot.command(help="Dig and gather resources.\nCan only be used if you have a shovel",
            brief="Dig and get resources",
            usage="{}dig".format(PREFIX),
            aliases=["d"])
async def dig(ctx):
    embed_var = discord.Embed(title="Digging", description=BotInfo.current_player.dig(), color=ctx.author.colour)
    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)


@bot.command(help="Fish... for fish.\nCan only be used if you have a fishing rod",
            brief="Fish... for fish",
            usage="{}fish".format(PREFIX),
            aliases=["f"])
async def fish(ctx):
    embed_var = discord.Embed(title="Fishing", description=BotInfo.current_player.fish(), color=ctx.author.colour)
    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)


@bot.command(help="Hunt and gather resources.\nCan only be used if you have a weapon",
            brief="Hunt and get resources",
            usage="{}hunt".format(PREFIX),
            aliases=["h"])
async def hunt(ctx):
    embed_var = discord.Embed(title="Hunting", description=BotInfo.current_player.hunt(), colour=ctx.author.colour)
    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)


@bot.command(help="Show the items in your inventory.\nUse the arrows to navigate.",
            brief="View your inventory",
            usage="{}inv or {}inventory".format(PREFIX, PREFIX),
            aliases=["inventory", "items", "viewitems"])
async def inv(ctx, other_user=None):
    # Show player's inventory

    if other_user is None:
        cur_page = 0

        unique_items = {}

        embed_var = discord.Embed(title="Inventory",
                                  description="Showing items in {}'s inventory:".format(ctx.author.mention),
                                  color=ctx.author.colour)
        embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        if len(BotInfo.current_player.inventory.get_items()) == 0:
            embed_var.add_field(name="No items", value="**You have no items in your inventory**")

            await ctx.send(embed=embed_var)
        else:

            for item in BotInfo.current_player.inventory.get_items():
                if item.get_id() in unique_items:
                    unique_items[item.get_id()] += 1
                else:
                    unique_items[item.get_id()] = 1

            pages_list = await split_into_pages(unique_items, 5)

            def populate_page(embed):
            
                for item in pages_list[cur_page]:

                    current_item = Item.get_item_by_id(item)

                    embed.add_field(name="{} - `{}`".format(current_item.get_name(), current_item.get_command_name()),
                                    value="{}\nQuantity: {}".format(current_item.get_description(), pages_list[cur_page].get(item)),
                                    inline=False)

            populate_page(embed_var)

            if len(pages_list) > 1:
                embed_var.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

            message = await ctx.send(embed=embed_var)

            if len(pages_list) > 1:
                await message.add_reaction("◀️")
                await message.add_reaction("▶️")

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                    # This makes sure nobody except the command sender can interact with the "menu"

                while True:
                    try:
                        reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)
                        # waiting for a reaction to be added - times out after x seconds, 60 in this
                        # example

                        if str(reaction.emoji) == "▶️":

                            cur_page += 1

                            if cur_page > len(pages_list) - 1:
                                cur_page = 0

                            new_embed = discord.Embed(title="Inventory",
                                                      description="Showing items in {}'s inventory:".format(
                                                          ctx.author.mention), color=ctx.author.colour)
                            new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                            populate_page(new_embed)

                            new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                            await message.edit(embed=new_embed)
                            await message.remove_reaction(reaction, user)

                        elif str(reaction.emoji) == "◀️":

                            cur_page -= 1

                            if cur_page < 0:
                                cur_page = len(pages_list) - 1

                            new_embed = discord.Embed(title="Inventory",
                                                      description="Showing items in {}'s inventory:".format(
                                                          ctx.author.mention), color=ctx.author.colour)
                            new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                            populate_page(new_embed)

                            new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                            await message.edit(embed=new_embed)
                            await message.remove_reaction(reaction, user)

                    except asyncio.TimeoutError:
                        await message.delete()
                        break
                        # ending the loop if user doesn't react after x seconds
    else:
        embed_var = discord.Embed(title="Information",
                                  description="{} viewing other people's inventory is not available at the moment"
                                  .format(ctx.author.mention), color=ctx.author.colour)
        
        await ctx.send(embed=embed_var)


@bot.command(name="clearinv", hidden=True)
@commands.check_any(commands.is_owner())
async def clear_inv(ctx, arg=None):
    if arg is None:
        BotInfo.current_player.clear_inventory()

        embed_var = discord.Embed(title="Information",
                                  description="**{} your inventory has been cleared.**".format(ctx.author.mention),
                                  color=ctx.author.colour)

    else:
        embed_var = discord.Embed(title="Information",
                                  description="**{} currently not implemented.**".format(ctx.author.mention),
                                  color=ctx.author.colour)
        print("Removing other people's inventory has not yet been implemented.")

    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)


@bot.command(name="recipes",
            help="View all the recipes that can be crafted.\nUse the arrows to navigate",
            brief="View all recipes",
            usage="{}recipes or {}reps".format(PREFIX, PREFIX),
            aliases=["reps"])
async def all_recipes(ctx):
    cur_page = 0

    embed_var = discord.Embed(title="All recipes",
                              description="{} showing all items which can be crafted:".format(ctx.author.mention),
                              color=ctx.author.colour)
    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    pages_list = await split_into_pages(JsonHandler.get_recipes(), 4)

    def populate_page(embed):

        for item in pages_list[cur_page]:
            recipe_string = "_**Command name**_: `{}`\n_**Required items**_:\n".format(item["command-name"])

            unique_items = {}

            for required_item in item["required-items"]:
                # Counting the required items

                if required_item["name"] in unique_items:
                    unique_items[required_item["name"]] += 1
                else:
                    unique_items[required_item["name"]] = 1

            for required_item in unique_items:
                recipe_string += "+ {} - {}\n".format(required_item, unique_items.get(required_item))

            embed.add_field(name=item["name"], value=recipe_string, inline=False)

    populate_page(embed_var)

    if len(pages_list) > 1:
        embed_var.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

    message = await ctx.send(embed=embed_var)

    if len(pages_list) > 1:

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)
                # waiting for a reaction to be added - times out after 30

                if str(reaction.emoji) == "▶️":

                    cur_page += 1

                    if cur_page > len(pages_list) - 1:
                        cur_page = 0

                    new_embed = discord.Embed(title="All recipes",
                                              description="{} showing all items which can be crafted:".format(
                                                  ctx.author.mention),
                                              color=ctx.author.colour)
                    new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                    populate_page(new_embed)

                    new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                    await message.edit(embed=new_embed)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️":

                    cur_page -= 1

                    if cur_page < 0:
                        cur_page = len(pages_list) - 1

                    new_embed = discord.Embed(title="All recipes",
                                              description="{} showing all items which can be crafted:".format(
                                                  ctx.author.mention),
                                              color=ctx.author.colour)
                    new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                    populate_page(new_embed)

                    new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                    await message.edit(embed=new_embed)
                    await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await message.delete()
                break
                # ending the loop if user doesn't react after x seconds


@bot.command(name="myrecipes",
            help="View all the items which you can make\nUse the arrows to navigate",
            brief="View items you can make",
            usage="{}myrecipes or {}mr".format(PREFIX, PREFIX),
            aliases=["mr"])
async def my_recipes(ctx):
    cur_page = 0

    embed_var = discord.Embed(title="Recipes", description="Showing items {} can make:".format(ctx.author.mention),
                              color=ctx.author.colour)
    embed_var = embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    craftable_items = BotInfo.crafting_system.get_craftable_items()

    if len(craftable_items) == 0:
        embed_var.add_field(name="No items", value="**You do not have the resources to craft any items**")

        await ctx.send(embed=embed_var)
        return
    else:

        pages_list = await split_into_pages(craftable_items, 5)

        def populate_page(embed):

            for craftable_item in pages_list[cur_page]:
    
                embed.add_field(name=craftable_item["name"],
                                    value="`{}` - Quantity: {}".format(craftable_item["command-name"],
                                    craftable_item["quantity"]),
                                    inline=False)

        populate_page(embed_var)

        if len(pages_list) > 1:
            embed_var.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

        message = await ctx.send(embed=embed_var)

        if len(pages_list) > 1:
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                # This makes sure nobody except the command sender can interact with the "menu"

            while True:
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)

                    if str(reaction.emoji) == "▶️":

                        cur_page += 1

                        # Rollback page to the first if page counter exceed max pages
                        if cur_page > len(pages_list) - 1:
                            cur_page = 0

                        new_embed = discord.Embed(title="Recipes",
                                                  description="Showing items {} can make:".format(ctx.author.mention),
                                                  color=ctx.author.colour)

                        new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)


                        populate_page(new_embed)

                        new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                        await message.edit(embed=new_embed)
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️":

                        cur_page -= 1

                        # Roll forward page to the last if page counter is less than zero
                        if cur_page < 0:
                            cur_page = len(pages_list) - 1

                        new_embed = discord.Embed(title="Recipes",
                                                  description="Showing items {} can make:".format(ctx.author.mention),
                                                  color=ctx.author.colour)
                        new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                        populate_page(new_embed)

                        new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                        await message.edit(embed=new_embed)
                        await message.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    await message.delete()
                    break
                    # ending the loop if user doesn't react after x seconds


@bot.command(help="Craft items with your gathered resources",
            brief="Craft items",
            usage="{}craft".format(PREFIX))
async def craft(ctx, item, amount = None):

    if amount is None:
        embed_var = discord.Embed(title="Crafting", description=BotInfo.crafting_system.craft_item(item),
                                color=ctx.author.colour)
    else:
         embed_var = discord.Embed(title="Crafting", description=BotInfo.crafting_system.craft_item(item, amount),
                                color=ctx.author.colour)

    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)


@craft.error
async def craft_error(ctx, error):
    
    embed_var = None

    if isinstance(error, commands.MissingRequiredArgument):
        embed_var = discord.Embed(title="Crafting",
                                  description="{} incorrect use of command. Please use `{}craft <item name> <(optional) amount>`.".format(
                                      ctx.author.mention, PREFIX), color=ctx.author.colour)

    await ctx.send(embed=embed_var)


@bot.command(name="smeltable",
            help="View all the items which you can smelt in your inventory.\nUse the pages to navigate",
            brief="View all your smeltable items",
            usage="{}smeltable".format(PREFIX))
async def get_smeltable(ctx):

    cur_page = 0

    smeltable_items = BotInfo.crafting_system.get_smeltable_items()

    embed_var = discord.Embed(title="Smeltable Items", description="Showing items that {} can smelt:".format(ctx.author.mention),
                                color=ctx.author.colour)
    embed_var = embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    if len(smeltable_items) == 0:
        embed_var.add_field(name="No items", value="**You do not have the resources to smelt any items**")

        await ctx.send(embed=embed_var)
        return

    pages_list = await split_into_pages(smeltable_items, 5)

    def populate_page(embed):
        for smeltable_item in pages_list[cur_page]:

            current_item = Item.get_item_by_id(smeltable_item)
            smelt_item = Item.get_item_by_id(current_item.get_smelted_item_id())

            if current_item == None or smelt_item == None:
                break
            
            embed.add_field(name="{} :arrow_right: {}".format(current_item.name, smelt_item.name), 
                                value="`{}` - Quantity: {}".format(current_item.command_name, smeltable_items.get(smeltable_item)),
                                inline=False)


    populate_page(embed_var)

    if len(pages_list) > 1:
        embed_var.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

    message = await ctx.send(embed=embed_var)

    if len(pages_list) > 1:
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)

                if str(reaction.emoji) == "▶️":

                    cur_page += 1

                    # Rollback page to the first if page counter exceed max pages
                    if cur_page > len(pages_list) - 1:
                        cur_page = 0
                        
                    new_embed = discord.Embed(title="Smeltable Items",
                                              description="Showing items that {} can smelt:".format(ctx.author.mention),
                                              color=ctx.author.colour)

                    new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                    populate_page(new_embed)

                    new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                    await message.edit(embed=new_embed)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️":

                    cur_page -= 1

                    # Roll forward page to the last if page counter is less than zero
                    if cur_page < 0:
                        cur_page = len(pages_list) - 1

                    new_embed = discord.Embed(title="Smeltable Items",
                                              description="Showing items {} that can smelt:".format(ctx.author.mention),
                                              color=ctx.author.colour)

                    new_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

                    populate_page(new_embed)

                    new_embed.set_footer(text="Page {}/{}".format(str(cur_page + 1), str(len(pages_list))))

                    await message.edit(embed=new_embed)
                    await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await message.delete()
                break
                # ending the loop if user doesn't react after x seconds


@bot.command(help="Smelt your items to create something new",
            brief="Smelt items",
            usage="{}smelt".format(PREFIX))
async def smelt(ctx, item, amount = None):
    
    embed_var = None

    if amount is None:
        embed_var = discord.Embed(title="Smelting", description=BotInfo.crafting_system.smelt_item(item),
                                color=ctx.author.colour)
    else:
        embed_var = discord.Embed(title="Smelting", description=BotInfo.crafting_system.smelt_item(item, amount),
                                color=ctx.author.colour)

    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)

@smelt.error
async def smelt_error(ctx, error):
    
    embed_var = None

    if isinstance(error, commands.MissingRequiredArgument):
        embed_var = discord.Embed(title = "Smelting",
                                    description="{} incorrect use of command. Please use `{}smelt <item name> <(optional) amount>`".format(
                                        ctx.author.mention, PREFIX), color=ctx.author.colour)

    await ctx.send(embed=embed_var)


@bot.command(name="addfuel",
            help="Take resources from your inventory to add to your fuel stockpile",
            brief="Add fuel to your fuel stockpile",
            usage="{}addfuel or {}af".format(PREFIX, PREFIX),
            aliases=["af"])
async def add_fuel(ctx, item, amount=None):
    
    if amount is None:
        embed_var = discord.Embed(title="Adding Fuel",
                                 description=BotInfo.crafting_system.add_fuel(item),
                                 color=ctx.author.colour)
    else:
        embed_var = discord.Embed(title="Adding Fuel",
                                 description=BotInfo.crafting_system.add_fuel(item, amount),
                                 color=ctx.author.colour)

    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed_var)

@add_fuel.error
async def add_fuel_error(ctx, error):

    embed_var = discord.Embed(title="Adding Fuel",
                                  description="An unknown error has occured.".format(
                                      ctx.author.mention, PREFIX), color=ctx.author.colour)

    if isinstance(error, commands.MissingRequiredArgument):
        embed_var = discord.Embed(title="Adding Fuel",
                                  description="{} incorrect use of command. Please use `{}addfuel <item name>`.".format(
                                      ctx.author.mention, PREFIX), color=ctx.author.colour)

    await ctx.send(embed=embed_var)


@bot.command(name="stats",
            help="Use this command to show key statistics about the player.",
            brief="Show info about the player",
            usage="{}stats or {}statistics".format(PREFIX, PREFIX),
            aliases=["statistics"])
async def statistics(ctx):
    
    embed_var = discord.Embed(title="Statistics", description="Showing stats for {}".format(ctx.author.mention),
                              color=ctx.author.colour)
    embed_var.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    embed_var.add_field(name="Current Health", value=str(BotInfo.current_player.current_health), inline=True)
    embed_var.add_field(name="Current Armour", value=str(BotInfo.current_player.current_armour), inline=True)
    embed_var.add_field(name="Number of Items", value=str(len(BotInfo.current_player.inventory.get_items())),
                        inline=True)
    embed_var.add_field(name="Fuel", value=str(BotInfo.current_player.get_fuel_amount()),
                        inline=True)

    await ctx.send(embed=embed_var)


bot.run(discord_token)
