# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("You")
define d = Character("{i}You")


# The game starts here.

label start:

    # Show a background. This uses a placeholder by default, but you can
    # add a file (named either "bg room.png" or "bg room.jpg") to the
    # images directory to show it.

    scene bg sidewalk
    play music "city_music.mp3" fadein 1.5

    # This shows a character sprite. A placeholder is used, but you can
    # replace it by adding a file named "eileen happy.png" to the images
    # directory.

    

    # These display lines of dialogue.

    "It has been a long day, speaking with strangers and trying to sell them cookies,"

    e "The Cookie Crumble, with all the latest flavors!"

    "There's been a couple of bites, but many have declined the cookies, claiming to bake their own cookies."

    "As you are walking, you come to the final house on your route."

    "Double checking the address, you pause,"

    e "I guess this is the place. It looks a little run down though." 

    scene bg house_fa 

    "You've seen worse houses, usually in the newspaper. The grass has grown wild, the windows are covered up, and the gutters are full of dead leaves."

    e "Does anybody actually live here?"

    "The path to the front door is choked with weeds, and you decided to wear shorts today."

    e "Just my luck!"

    menu optional_name:
        "What should I do?"
        "Continue Walking":
            scene bg sidewalk
            e "Well it's getting late. I don't think anybody lives here after all."
            "Turning away, you leave the house behind. When you reach the end of the block, a sudden wind comes from behind, pushing at you."
            "Looking back, you see nothing out of the ordinary."
            e "That was weird."
            "Shaking your head, you return to walking."
            "You'll take the bus home, and that night, you sleep soundly. You've done a lot of walking today, and tomorrow's a new day."
            jump end_credits


        "Approach the Door":
            scene bg door
            play music "suspense.mp3" fadein 1.5
            "Fighting your way through the weeds, you climb up the steps to stand in front of the door." 
            "There's an ancient doorbell to the right, and beyond that a window. The lights are off, and it looks like something has been put over the window, but a small, dark hole exists."
            e "Is anybody home?" #shouting character 
            menu:
                "What should I do?"
                "Knock on the door":

                    "You go to knock on the door, but your hand passes through the air as the door opens."

                    jump rejoin_text

                "Try the Doorknob":
                    "Who tries the doorknob to an abandoned house? You, apparently, and you are rewarded by the door opening soundlessly."
                    jump rejoin_text
    
    label rejoin_text: 
    scene bg door_cl

    "{i}Thats weird.{i}"

    play music "dread.mp3" fadein 1.5

    e "Is anybody home?" #shouting character

    "As you look through the doorway, you hear a loud {b}THUMP{/b} from above you, like someone falling off a bed."

    e "Is everything alright?" 

    scene bg door_op
    
    "You take step inside the door, towards the stairs,"

    e "Did somebody just fall?" #confused character

    "Suddenly a wind blows , seemingly from down the stairs, and the door slams shut behind you with a BANG."

    show rabbit

    "Spinning, you realize that she's something standing between you and the door; it's easily as tall as the ceiling, even taller, with long, shadowy arms and a big, misshapen head of darkness. Ivory-colored eyes shine, and then there's nothing."

    #dead end
    #perspective shift

    scene bg sidewalk
    play music "city_music2.mp3" fadein 1.5


    "You've had a long day selling brochures, going from door to door."

    d "This is the last house on the block."

    scene bg house_sp
    play music "suspense.mp3" fadein 1.5

    "You look up to see a two-story building, with what looks like an attic on top of that."

    d "I guess this is the place."

    scene bg door
    play music "dread.mp3" fadein 1.5
    
    label end_credits: 

    scene end
    play music "end.mp3" fadein 1.5

    "Story by Tyler Bar-Ness"
    "Game Design by Lucas Vinet"
    "Art by Tyler Bar-Ness"
    "Coding by AJ Ristino"
    "Translations by, AJ Ristino, Enjin Wang, Tyler Bar-Ness, and Lucas Vinet"
    "Music by {i}Universfield, DELOsound, |cl21, BackgroundMusicForVideo{/i}"

    "The End."


    return
