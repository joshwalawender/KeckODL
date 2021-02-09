# Observing Description Language

The Keck Observing Description Language (ODL) is used to describe an observation for the Database Driven Observing Initiative (DDOI) which is part of the Data Services Initiative (DSI) project at Keck.

# Goals

The ODL must be capable of encoding a complete set of instructions to run an observation without additional human decision making.  Human interaction may be needed for steps such as target acquisition (for example: aligning the target on the slit or running mask alignment).

For normal operations, users will not interact directly with this language: it will be produced by the Observing Definition Tool and stored in the Observing Database. From there, observations will be retrieved and sent to the observing tools. An exception to this model is the possibility of linking our observing infrastructure to large surveys or to TOMs: in this case, it is likely that those users will produce observing sequences directly in the required format and submit them to our database using an API.


# The Language

Since the ODL is a language it should have elements of a language: vocabulary, syntax, grammar, and a written form.

## Vocabulary

#### High Level Concepts

- `ObservingBlock` (OB): This is the atomic operation which the observer will execute at night.
- `ObservingBlockList`: Just a simple ordered list of OBs.
- `Target`: Observers know this because it inherits all properties of targets in star lists.
- `Alignment`: This is how you put your target in the position you want it (i.e. in a slit).
- `InstrumentConfig`: This is how the instrument is configured.
- `DetectorConfig`: This is how the detector is configured.
- `OffsetPattern`: The dither pattern to use during observation.

The `InstrumentConfig` and `DetectorConfig` have been separated out as two concepts because the standard calibrations we take are based entirely on the `InstrumentConfig`.

#### Low Level Concepts

- Observing blocks have types:
    - `ScienceBlock`
    - `StandardStarBlock`
    - `TelluricBlock`
    - `CalibrationBlock`
    - `FocusBlock` (e.g Mira or Autofoc)
- Alignment can be done in multiple ways
    - `BlindAlign`
    - `GuiderAlign`
    - `MaskAlign`
- An offset pattern contains other concepts
    - `OffsetFrame` (e.g. sky frame, instrument frame, slit frame)
    - `TelescopeOffset`

## Syntax and Grammar

I won't lay out all the rules here, but for example, an `ObservingBlock` is comprised of:

- 0 or 1 Targets
- 1 OffsetPattern
- 1 Instrument Configuration
- 0 or more Detector Configurations
- 0 or 1 Alignment

The behavior of the system will depend on which of these are specified.

The `ObservingBlockList` is **ordered**, so it can be used to describe an order of operations, but fundamentally, the observer simply selects an OB to execute, so no higher order scheduling is implemented here.  If we want scheduling that is more sophisticated that this, we simply add a higher level component (e.g. the "Minimum Schedulable Block" or MSB) which is an ordered list of OBs, but has some extra scheduling metadata attached to it.

## Written Form

YAML or JSON are easy written forms to implement because the language is composed of dictionaries (key-value pairs) and lists.  I used YAML because it allows for comments in case some advnaced users want to write the YAML form directly, but I expect that won't be common.

There are some `__str__` representations which are more human readbale, but which are not complete specifications; they are meant to be reminders.

In its final form, each instance of an object would be given a unique ID of some sort to identify it rather than using the name string as we do here.





# Elements of the ODL

## Observing Block

An "Observing Block" (OB) fully describes a coherent observation of a target.  An observing night and its associated calibrations consists of a series of Observing Blocks.

In its simplest form an Observing Block contains enough information so that the telescope operator and visiting scientist can execute an observation of a single target with minimal additional human input.

An Observing Block is comprised of 
- 0 or 1 Targets
- 1 OffsetPattern
- 1 Instrument Configuration
- 1 or more Detector Configurations
- 1 Alignment

These components and their sub-components are described below.

An OB comes in one of several types, represented by sub-classes.  Thus the `ObservingBlock` class itself is an abstract class which should be sub-classed in normal use.

### Observing Block Types

`ScienceBlock`: An OB representing a science observation.

`TelluricBlock`: An OB representing a telluric standard observation.

`StandardStarBlock`: An OB representing a standard star observation.

`CalibrationBlock`: An OB representing a calibration observation (e.g. arc lamps or dome flats).

`FocusBlock`: An OB representing a telescope focus operation.


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

The `keckODL.instrument_config.InstrumentConfig` is an object to hold information describing the instrument.  It is intended to be subclassed for each instrument at Keck.

An instrument's control system should be able to take an instance of this object and then configure the instrument appropriately.  This has intellectual heritage with the `save_state` and `restore_state` scripts used on some existing Keck instruments.

## Detector Configuration

The `keckODL.detector_config.DetectorConfig` is an object to hold information describing a particular detector's configuration.  Similar to the `InstrumentConfig` above it has some conceptual heritage from the `save_state` and `restore_state` scripts.

The `DetectorConfig` object is abstract and is sub-classed in to two additional classes: `IRDetectorConfig` and `VisibleDetectorConfig`.  Each of those is expected to be subclassed for a particular instrument's detector.

The high level `DetectorConfig` class contains only a few basic concepts such as exposure time, readoutmode (which is interpreted differently by different instruments), and number of exposures.

The number of exposures property is how one would configure an Observing Block to take multiple exposures at each point in a dither pattern before moving on to the next position in the pattern.

#### IRDetectorConfig

The `IRDetectorConfig` sub-class adds the additional property of coadds which is common to IR detectors.

#### VisibleDetectorConfig

The `VisibleDetectorConfig` sub-class adds additional properties common to CCD detectors such as binning, windowing, ampmode, and dark.

## Alignment

The `keckODL.alignment.Alignment` is an object to hold information about how to align the telescope on target.  While much of this processis handled by humans (either the OA or the observer depending on the alignment method and instrument), it is useful to allow for information on how to align to be carried around in the OB for re-use.

One of the primary areas where this may be useful is in the mask alignment process.  Having an `Alignment` object contain the filter and exposure information may be useful.  In the vast majority of cases, however, we expect the observer to simply choose a method and accept the default arguments.

#### BlindAlign

The `keckODL.alignment.BlindAlign` object specifies a "blind" alignment.  A BlindAlign will slew the telescope to the target and perform no additional alignment steps.

A similar, but distinct alignment strategy would be a `None` object (instead of some instance of an `Alignment`) which means do not slew the telescope.  It is meant to indicate that the telescope should not be moved because it is already aligned.  One would use this, for example, for a second OB on the same mask with different instrument or detector configurations because the mask was aligned in the previous OB.

#### GuiderAlign

The `keckODL.alignment.GuiderAlign` object specifies an alignment using the slit viewing or guide camera.  Note that whether the alignment uses an offset star is still encoded in the `Target` instance for compatibility with traditional Keck starlists.

The only argument for an instance of `GuiderAlign` is the boolean value for `bright` which defaults to True.  How to handle the value of faint varies by instrument, but for a normal slit viewing guider (e.g. LRIS or ESI), if bright is False, that indicates to the OA that the guide exposure may need to be increased.

Anoher use of the bright flag would be for IR slit viewing cameras (e.g. NIRES), where the bright flag being set to False would indicate the need to do a sky subtracted pair to identify the target.

#### MaskAlign

The `keckODL.alignment.MaskAlign` object specifies an alignment using the Slitmask Alignment Tool (or similar software).  This alignment is done using one of the science detectors in the instrument.  Thus one of the arguments for this object is `detconfig` which would contain a `DetectorConfig` instance.  This allows the observer to choose the detector parameters for the alignment (e.g. exposure time, number of coadds, etc.).

Other arguments for this object include the boolean `takesky` to control whether a sky frame should be taken (typical for IR instruments), and an argument `filter` to specify which filter should be used for the alignment images.

As with a `GuiderAlign`, the `Target` properties can specify that this can be done on an offset star.  This is unusual with this alignment method, but has been done with MOSFIRE for example.  In that case, the offset would be aplpied after the alignment process is complete.
