
# ⛧ NNA - Node Name Abuse ⛧
## Blender 4.2+ Tooling
### Early in development version, do not use productively!

**Find the Unity counterpart here: <https://github.com/emperorofmars/nna_unity>**

---

Extend any 3d format by abusing node-names.\
This works by naming nodes in a specific way, and by serializing JSON into node-names.

This project is an abomination and the sooner it can burn in a fire, the better.

⭐ Star this repo if you love heresy! ⭐

![](./Docs/img/nna-example.png)
![](./Docs/img/nna-blender.png)

Issues, discussions & PRs Welcome!

## Why
Existing 3d interchange formats are bad. The least horrible one, FBX, is not extensible.

This is a way to add additional information to 3d models in any format, primarily FBX.
Use this Blender Addon to create and edit NNA JSON definitions.

### Goals
* A 3d file should be a self-contained single source of truth for all its functionality, and work across different game engines.
* Artists without too much technical knowledge beyond 3d modeling, should have an easy time creating VR avatars.
* End users without too much technical knowledge, should be able to easily adapt and upload their avatars.

## How
For simpler definitions, information can be encoded into a node name directly.\
For more complex components, you can serialize JSON into an array of child-nodes. This addon will help you work with that.

On import into a game-engine with an NNA implementation, these definitions will be parsed into the game-engines own constructs.

Additional processors can be easily implemented, even in completely separate packages, and automatically hot-loaded.

### Name Definitions
Name definitions must if inside of a single node-name.
Their format is different for each definition but follows the following general syntax:

**Syntax:** `Actual Node Name` `NNA Processor Name` `Optional Parameters` `Optional Symmetry Suffix`

*Example:* `UpperLegTwistHips0.5.R`

`UpperLeg` is the actual node name.
`Twist` is the NNA processor name.
`Hips` is a parameter for the processor.
`0.5` is a parameter for the processor.
`.R` signifies the right side of the model.

### Json Definitions
Json definitions are of arbitrary length, as they are spread over multiple nodes.\
They are an array of components, all of which must have a `t` property. It specifies the 'type' of the component, based upon which it will be processed.\
On import, after they have been processed, they will be removed from the hierarchy by default.\
They should be contained in a single node named `$nna`, which should be parented to the root.

*Example*:\
`$nna`\
→ `$target:Hair01`\
→ → `$0$[{"t":"ava.secondary_motion","id":"0","intensity":0.4},{"t`\
→ → `$1$":"vrc.physbone", "overrides":["0"],"pull":0.15,"spring":0`\
→ → `$2$.3,"limit_type":"angle","max_angle":60}]`

Json components can have optional `id` and `overrides` properties.\
An `id` is a string that must be unique within the model, and can be used to reference other components.\
`overrides` is an array of ID's. The overridden components will not be processed.

## Current Status
The structure is pretty much there, and specific functionality is being worked on.

### Stage 1: MVP
Export decently featured VR avatars into `*.nna.fbx` files Some resources like animations, animation logic or materials will be mapped by name int the game-engine project.

The 'export from Blender, drag into Unity, and get a ready to upload VR avatar' experience is generally there, but the file depends on resources in the Unity project.

#### TODO
* More constraint types.
* More VR & V-tubing avatar components & features.
	* Bone based eyelid animation.
	* VRChat avatar colliders
	* Bone physics libraries: VRC Physbones & VRM Springbones.

### Stage 2: All In One
An `*.nna.fbx` file no longer needs external dependencies, other than NNA itself, in order to be parsed into a fully featured VR avatar.

A lot of these features are blocked by Blender's (lack of an) animation system. Will be fixed once Blender 4.4 is released with 'slotted actions'.

#### TODO
* More constraint types.
* Unity humanoid muscle settings.
* Animations, including being able to target NNA properties. (Blocked until Blender 4.4)
* Implement [MTF](https://github.com/emperorofmars/stf-unity/tree/master/MTF) to fully encode shader & game engine agnostic materials.
* More VR & V-tubing avatar components & features.
	* Bone physics (ava.secondary_motion as universal fallback, VRC Physbones & colliders & contacts, VRM spring bones & colliders, maybe DynamicBones & MagickaCloth)
	* Automatic animator controller generation (Partially blocked until Blender 4.4)
		* Face Tracking
		* Hand gestures (additionally: fallback VRM blendshape pose nonsense)
		* Toggles
		* Joystick puppets
		* Custom application & game engine agnostic animation logic

### Stage 3: Overlord
Go beyond what VR & V-Tubing applications support out of the box.

#### TODO
* Template system. (To apply user modifications. This would be the basis of a 'character editor' system, so end users could adapt their avatars easier.)
	* Gesture rebinding!
* Addon system. (To apply a piece of clothing from a separate file to a base body for example. This should be deeply integrated with the avatar components and the template system.)
* IDK, suggest me more!

---

I am disgusted by myself for making this.

Cheers!

Or something.