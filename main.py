import logging
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Set up logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),  # Log to a file
        logging.StreamHandler()            # Log to console
    ]
)

app = Ursina()

# Create a player entity using FirstPersonController
player = FirstPersonController()
player.position = (8, 10, 8)  # Positioned above the ground
logging.debug('Created player entity at position: {}'.format(player.position))

# Dictionary to store placed blocks for quick lookup
block_dict = {}

# Function to create terrain
def create_terrain(width, height):
    for x in range(width):
        for z in range(height):
            # Create bedrock
            create_block(BedrockBlock, (x, 0, z))

            # Create stone blocks above bedrock
            for y in range(1, 6):
                create_block(StoneBlock, (x, y, z))

            # Create dirt blocks above stone
            for y in range(6, 11):
                create_block(DirtBlock, (x, y, z))

            # Create grass block on top of dirt
            create_block(GrassBlock, (x, 11, z))

# Helper function to create blocks and store them in block_dict
def create_block(block_type, position):
    block = block_type(position=position)
    block_dict[position] = block
    logging.info(f'Created {block_type.__name__} at {position}')

# Grass block class
class GrassBlock(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='cube',
            position=position,
            texture='textures/grass_top',
            collider='box'
        )

# Dirt block class
class DirtBlock(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='cube',
            position=position,
            texture='textures/dirt',
            collider='box'
        )

# Stone block class
class StoneBlock(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='cube',
            position=position,
            texture='textures/stone',
            collider='box'
        )

# Bedrock block class
class BedrockBlock(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='cube',
            position=position,
            texture='textures/bedrock',
            collider='box'
        )

# Ghost block for previewing block placement
class GhostBlock(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='cube',
            position=position,
            color=color.azure,
            opacity=0.5,
            collider='box'
        )

# Create a ghost block and store current block type
ghost_block = GhostBlock(position=(0, -10, 0))  # Initially off-screen
block_types = [GrassBlock, DirtBlock, StoneBlock]
current_block_type = 0  # Index for the current block type

# Distance-based frustum culling: Only render blocks close to the camera
def is_within_range(entity, max_distance=20):
    distance = distance_xz(player.position, entity.position)
    return distance <= max_distance

# Function to place or break a block efficiently with distance-based frustum culling
def update():
    global ghost_block, current_block_type

    # Check all blocks in the scene and apply distance-based frustum culling
    for position, block in block_dict.items():
        block.visible = is_within_range(block)

    block_pos = mouse.world_point
    if block_pos is not None:
        # Snap ghost block to a grid
        rounded_pos = Vec3(round(block_pos.x), round(block_pos.y), round(block_pos.z))
        if ghost_block.position != rounded_pos:  # Only update if necessary
            ghost_block.position = rounded_pos

        # Place a block when left mouse button is held down
        if held_keys['left mouse'] and rounded_pos not in block_dict:
            create_block(block_types[current_block_type], rounded_pos)
            logging.info(f'Block placed at: {rounded_pos}')

        # Break a block when right mouse button is held down
        if held_keys['right mouse'] and rounded_pos in block_dict:
            block_dict[rounded_pos].disable()
            del block_dict[rounded_pos]
            logging.info(f'Block broken at: {rounded_pos}')

    # Change block type using number keys
    if held_keys['1']:
        current_block_type = 0  # GrassBlock
    elif held_keys['2']:
        current_block_type = 1  # DirtBlock
    elif held_keys['3']:
        current_block_type = 2  # StoneBlock

# Create initial terrain
create_terrain(16, 16)

# Hide the mouse cursor
app.mouse.visible = False

logging.info('Starting the Ursina app...')
app.run()
