from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import logging

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)

app = Ursina()

# Player setup
player = FirstPersonController()
player.position = (8, 10, 8)
logging.debug('Created player entity at position: {}'.format(player.position))

# Block types
class Block(Entity):
    def __init__(self, position=(0, 0, 0), texture='white_cube'):
        super().__init__(
            model='cube',
            texture=texture,
            position=position,
            collider='box'
        )

class GrassBlock(Block):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(position=position, texture='textures/grass_top')
        logging.info('Created GrassBlock at position: {}'.format(position))

class DirtBlock(Block):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(position=position, texture='textures/dirt')
        logging.info('Created DirtBlock at position: {}'.format(position))

class StoneBlock(Block):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(position=position, texture='textures/stone')
        logging.info('Created StoneBlock at position: {}'.format(position))

# Ghost block
class GhostBlock(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='cube',
            color=color.azure,
            opacity=0.5,
            position=position,
            collider='box'
        )
        self.visible = False  # Initially hide the ghost block

ghost_block = GhostBlock()  # Create ghost block instance
block_types = [GrassBlock, DirtBlock, StoneBlock]
current_block_type = 0

# Function to create terrain
def create_terrain(width, height):
    for x in range(width):
        for z in range(height):
            BedrockBlock(position=(x, 0, z))
            for y in range(1, 6):
                StoneBlock(position=(x, y, z))
            for y in range(6, 11):
                DirtBlock(position=(x, y, z))
            GrassBlock(position=(x, 11, z))

# Bedrock block class
class BedrockBlock(Block):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(position=position, texture='textures/bedrock')
        logging.info('Created BedrockBlock at position: {}'.format(position))

# Update function to handle block placement and breaking
def update():
    global current_block_type

    # Raycast to detect what block the player is pointing at
    if mouse.world_point is not None:
        hit_info = raycast(camera.world_position, camera.forward, distance=10, ignore=[ghost_block])

        if hit_info.hit:
            # Align ghost block to be placed on top of the surface hit
            hit_position = hit_info.entity.position
            hit_normal = hit_info.normal  # This will give us the direction to place the new block
            
            # Adjust the ghost block's position to the top surface of the hit block
            ghost_block.position = hit_position + hit_normal

            # Show ghost block only if there is no block already in that position
            ghost_block.visible = not any([entity.position == ghost_block.position for entity in scene.entities])

            # Place block with left mouse button
            if held_keys['left mouse'] and ghost_block.visible:
                # Place the block if the ghost block is visible (not colliding)
                if not any([entity.position == ghost_block.position for entity in scene.entities]):
                    block_types[current_block_type](position=ghost_block.position)
                    logging.info(f'Block placed at: {ghost_block.position}')

            # Remove block with right mouse button
            if held_keys['right mouse']:
                for entity in scene.entities:
                    if entity.position == hit_position and isinstance(entity, Block):
                        destroy(entity)
                        logging.info(f'Block removed at: {hit_position}')
                        break

    # Switch block type
    if held_keys['1']:
        current_block_type = 0  # GrassBlock
    elif held_keys['2']:
        current_block_type = 1  # DirtBlock
    elif held_keys['3']:
        current_block_type = 2  # StoneBlock

# Create initial terrain
create_terrain(16, 16)

app.run()
