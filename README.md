# KeckODL

The Keck Observing Description Language (ODL) is used to describe an observation for the Database Driven Observing Initiative (DDOI) which is part of the Data Services Initiative (DSI) project at Keck.

# Goals

The ODL must be capable of encoding a complete set of instructions to run an observation without additional human decision making.  Human interaction may be needed for steps such as target acquisition (for example: aligning the target on the slit or running mask alignment).

For normal operations, users will not interact directly with this language: it will be produced by the Observing Definition Tool and stored in the Observing Database. From there, observations will be retrieved and sent to the observing tools. An exception to this model is the possibility of linking our observing infrastructure to large surveys or to TOMs: in this case, it is likely that those users will produce observing sequences directly in the required format and submit them to our database using an API.


# Elements of the ODL

## Observing Block

An "Observing Block" (OB) fully describes a coherent observation of a target.  An observing night and its associated calibrations consists of a series of Observing Blocks.

In its simplest form an Observing Block contains enough information so that the telescope operator and visiting scientist can execute an observation of a single target with minimal additional human input.

An Observing Block is comprised of 
- 0 or 1 Targets
- 1 OffsetPattern
- 1 Instrument Configuration
- 1 or more Detector Configurations

These components and their sub-components are described below.


## Target

A Target describes all the attributes needed to point the telescope and track a particular location in the sky.  

See the doc string for the `keckODL.target.Target` object for all the properties.

#### Keck Starlists

The `keckODL.target.Target` properties are strongly influenced by the [Keck starlist](https://www2.keck.hawaii.edu/realpublic/observing/starlist.html).  As a result, existing starlist files can be read in and ingested to create `keckODL.target.Target` objects though this new implementation contains a few features that did not exist for star lists

New Features (compared to a Keck Starlist):
- Handling of proper motions: a `keckODL.target.Target` can propagate a coordinate if given proper motions, an epoch, and a time to propgate to.
- A `from_name` method: since the coordinate component of a `keckODL.target.Target` is an `astropy.coordinates.SkyCoord` object, the `from_name` method of that object is supported.
- Due to the use of `astropy.coordinates.SkyCoord`, the `keckODL.target.Target` object can utilize the frames and detailed time concepts used there.


## Offset Pattern

A `keckODL.offset.OffsetPattern` describes a series of small telescope moves which are used during the observation of a single target.  Classical examples of these would be a dither pattern used in imaging (e.g. box5) or an offset pattern used for spectroscopy (e.g. ABBA).  Since this sequence of small moves would be done on a single target, this is one component of an Observing Block.

An offset pattern primarily consists of a number of repeats and a list of individual offsets.  It is assumed that one or more exposures is obtained at each position in the pattern as specified by the Detector Configuration used.

Several patterns are built in to the ODL as examples and for use:
- `Stare`: This is a simple pattern with no moves.  It would be used for observations where no dithering is desired or for calibrations.
- `StarSky`: A simple two point pattern which starts at the target of interest (the "star" position), the offsets to another position to sample the sky background (the "sky" position).
- `SkyStar`: Identical to the above `StarSky` pattern except that it begins at the "sky" position.
- `StarSkyStar`: Similar to the above two patters except it contains two "star" positions for each "sky" position yielding a greater fraction of time on target.

Many standard spectroscopic patterns which would be used to dither along a slit such as ABBA, ABB'A', mask nod, etc. are not part of the generic ODL, but are unique to each instrument because they must be aware of the instrument's slit based reference frame in order to make their telescope moves.  Thus they are contained in the particular sub-package for that instrument.

#### Telescope Offsets

Each of the offsets in an Offset Pattern consistes of a Telescope Offset which describes the amount of the mode to be made, the frame in which it should be made, whether the move is relative or absolute, and whether the telescope should
be guided at that position.  See the docstring for `keckODL.offset.TelescopeOffset` for details.


#### Frame

Each offset must be done in a particular coordinate frame.  The ODL contains an abstract `keckODL.offset.OffsetFrame` which is subclassed in to either a `keckODL.offset.SkyFrame` or a `keckODL.offset.InstrumentFrame` (others are also possible, but not yet implemented).

Offsetting using a `SkyFrame` would offset in sky coordinates (in cardinal directions).  Offsetting using an `InstrumentFrame` would offset in detector coordinates (in the directions of pixel rows or columns) or could be used to offset along a slit (which may or may not be along detector rows or columns).  Instantiating a `SkyFrame` with a scale argument would allow it to be used to offset in units such as pixels or millimeters.

These two frames are implemented at the keyword level.  The object specifies which keywords to use.  For example `RAOFF` & `DECOFF` are used for the `SkyFrame` and `INSTXOFF` & `INSTYOFF` for an `InstrumentFrame`.  An `InstrumentFrame` also contains a scale (arcseconds per pixel) so that either pixel or angular units can be used and it contains an angle (which could be used to describe the angle a slit makes to the detector pixels for example).


## Instrument Configuration



## Detector Configuration



