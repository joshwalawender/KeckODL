# KeckODL

The Keck Observing Description Language (ODL) is used to describe an observation for the Database Driven Observing Initiative (DDOI) which is part of the Data Services Initiative (DSI) project at Keck.

# Goals

The ODL must be capable of encoding a complete set of instructions to run an observation without additional human decision making.  Human interaction may be needed dor some steps such as target acquisition (for example: aligning the target on the slit or mask alignment).

For normal operations, users will not interact directly with this language: it will be produced by the Observing Definition Tool and stored in the Observing Database. From there, observations will be retrieved and sent to the observing tools. An exception to this model is the possibility of linking our observing infrastructure to large surveys or to TOMs: in this case, it is likely that those users will produce observing sequences directly in the required format and submit them to our database using an API.


# Elements of the ODL

## Observing Block

An "Observing Block" (OB) fully describes a coherent observation of a target (if specified).  An observing night and its associated calibrations can be described by a series of Observing Blocks.

In its simplest form an Observing Block contains enough information so that the telescope operator and visiting scientist can execute an observation of a single target with minimal additional human input.

An Observing Block is comprised of 
- 0 or 1 Targets
- 1 OffsetPattern
- 1 Instrument Configuration
- 1 or more Detector Configurations

These components are described individually below.


## Target

A Target describes all the attributes needed to point the telescope and track a particular in the sky.  

See the doc string for the `keckODL.target.Target` object for al the properties.

#### Keck Starlists

The `keckODL.target.Target` properties are strongly influenced by the [Keck starlist](https://www2.keck.hawaii.edu/realpublic/observing/starlist.html).  As a result, existing starlist files can be read in and ingested to create `keckODL.target.Target` objects though this new implementation contains a few features that did not exist for star lists

New Features (compared to a Keck Starlist):
- Handling of proper motions: a `keckODL.target.Target` can propagate a coordinate if given proper motions, and epoch, and a time to propgate to.
- A `from_name` method: since the coordinate component of a `keckODL.target.Target` is an `astropy.coordinates.SkyCoord` object, the `from_name` method of that object is supported.
- Due to the use of `astropy.coordinates.SkyCoord`, the `keckODL.target.Target` object can utilize the frames and detailed time concepts used there.


## Offset Pattern

An Offset Pattern describes a series of small telescope moves which are used during the observation of a single target.  Classical examples of these would be a dither pattern used in imaging (e.g. box5) or an offset pattern used for spectroscopy (e.g. ABBA).  Since this sequence of small moves would be done on a single target, this is one component of an Observing Block.

An offset pattern primarily consists of a number of repeats and a list of individual offsets.  It is assumed that one or more exposures is obtained at each position in the pattern as specified by the Detector Configuration used.

Several patterns are built in to the ODL as examples and for use:
- `Stare`: This is a simple pattern with no moves.  It would be used for observations where no dithering is desired or for calibrations.
- `StarSky`: A simple two point pattern which starts at the target of interest (the "star" position), the offsets to another position to sample the sky background (the "sky" position).
- `SkyStar`: Identical to the above `StarSky` pattern except that ot begins at the "sky" position.
- `StarSkyStar`: Similar to the above two patters except it contains two "star" positions for each "sky" position yielding a greater fraction of time on target.

Many standard spectroscopic patterns which would be used to dither along a slit such as ABBA, ABB'A', mask nod, etc. are not part of the ODL, but are unique to each instrument because they must be aware of the instrument's slit based reference frame in order to make their telescope moves.

#### Telescope Offsets

Each of the offsets in an Offset Pattern consistes of a Telescope Offset which consists of:

- `dx`: an offset (in arcseconds) in the X direction
- `dy`: an offset (in arcseconds) in the Y direction
- `dr`: an offset (in degrees) of rotation
- `frame`: the frame in which the offset is made (see below)
- `relative`: a boolean value indicating whether the offset is to be made relative to the current position or is an absolute offset (relative to the original target position).
- `posname`: A name for the position
- `guide`: a boolean value indicating whether to guide at that position

#### Frame

Each offset must be done in a particular coordinate frame.  The ODL contains an abstract `OffsetFrame` which is subclassed in to either a `SkyFrame` or an `InstrumentFrame` (others are also possible, but not yet implemented).

Offsetting using a `SkyFrame` would offset in sky coordinates (in cardinal directions).  Offsetting using an `InstrumentFrame` would offset in detector coordinates (in the directions of pixel rows or columns) or could be used to offset along a slit (which may or may not be along detector rows or columns).

These two frames are implemented at the keyword level.  The object specifies which keywords to use.  For example `RAOFF` & `DECOFF` are used for the `SkyFrame` and `INSTXOFF` & `INSTYOFF` for an `InstrumentFrame`.  An `InstrumentFrame` also contains a scale (arcseconds per pixel) so that either pixel or angular units can be used and it contains an angle (which could be used to describe the angle a slit makes to the detector pixels for example).


## Instrument Configuration



## Detector Configuration



