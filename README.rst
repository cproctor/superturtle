# Superturtle

Superturtle provides extensions to Python's `turtle` module, supporting richer drawing, 
image export, and animation.

## Installation

First, make sure ImageMagick is installed. (If you use homebrew, this can be accomplished 
with `brew install imagemagick`.) Then, Superturtle can be installed using pip or poetry.

    pip install superturtle

## Pedagogy

This module was originally developed as part of **Making With Code**, a constructionist
introductory computer science curriculum. Perhaps the most unusual design decision is this 
module's heavy use of context managers. Context managers are generally not introduced 
early in a CS curriculum, but they fit naturally with other constructs which contextualize
code blocks: loops, conditionals, and function definition. We hypothesize that introducing
context managers at the same time may help students 
