#!python3

## Import General Tools
from pathlib import Path
from warnings import warn
from collections import UserList
import yaml
from astropy import units as u
from astropy import coordinates as c
from astropy.time import Time


# List the valid values for the rotator mode, acquisition, and object types
rotator_modes = ['pa',
                 'stationary',
                 'vertical']
acquisition_modes = ['guider: bright',
                     'guider: faint',
                     'guider: offset',
                     'mask align',
                     'mask align + offset',
                     'blind',
                     'none']
object_types = ['science',
                'sky',
                'flux standard',
                'telluric standard',
                'cal',
                'custom']
valid_PAs = {'pa': [0, 360],
             'stationary': [0, 360],
             'vertical': [0, 360],
            }
cal_positions = ['none', 'domeflat', 'domeflats']
telescope_wraps = ['n', 's', 'north', 'south', 'shortest']


class TargetError(Exception): pass


class TargetWarning(UserWarning): pass


##-------------------------------------------------------------------------
## Target
##-------------------------------------------------------------------------
class Target():
    '''An object to contain all necessary information about a sidereal target.
    
    Attributes
    ----------
    name : string
        An arbitrary name for the target.  If no coordinates are given, the
        software will try to resolve the name using the `from_name` method of
        the `astropy.coordinates.SkyCoord` class.
    
    RA : float or str
        The right ascension in decimal degrees or a sexagesimal string in
        hours, minutes, and seconds (colon separated or space separated).
    
    Dec : float or str
        The Declination in decimal degrees or a sexagesimal string in degrees,
        arcminutes, and arcseconds (colon separated or space separated).
    
    equinox : float
        The equinox of the coordinate system as a decimal year.  If the frame
        attribute below is given as "icrs" (the default) this will default to
        a value of 2000.
    
    frame : string
        The frame in which the coordinates are defined.  Must be a valid value
        for ingestion as a `astropy.coordinates.SkyCoord` frame specifier.
        Defaults to "icrs".
    
    rotmode : string
        The rotator mode to use for the observation.  Must be one of 'pa',
        'stationary', 'vertical'.
    
    PA : float
        The position angle in degrees for the rotator mode specified above.
    
    RAOffset : float
    DecOffset : float
        The value in arcseconds to offset East/West or North/South from the
        given RA and Dec coordinate to get to the target,
    
    objecttype : string
        The type of object.  Must be one of 'science', 'sky', 'flux standard',
        'telluric standard', 'custom'.
    
    acquisition : string
        The acquisition strategy for this target.  Must be one of
        'guider: bright', 'guider: faint', 'guider: offset', 'mask align',
        'blind'.  Definitions for those are below.
    
    PMRA : float
    PMDec : float
        The proper motion of the target in arcseconds per year.
    
    epoch : float
        The epoch in decimal year of the coordinate.  Used to propagate the
        coordinate from the position at the epoch to the position at a given
        observing time (see below).
    
    obstime : float
        The time in decimal year to which the proper motion should be
        propagated.  Defaults to now.
    
    mag : dict
        A dictionary of band (str) and magnitude (float) values.
    
    wrap : str or None
        Values of "shortest", "south", or "north" are valid. None will be
        interpreted as "shortest".  South is clockwise with az increasing and
        north is counterclockwise with az decreasing.
    
    dra : float
        RA differential tracking rate in arcsec/hr divided by 15 (positive
        implies moving east).  This is the backwards compatible way of
        supporting non-sidereal targets.  We plan to add additional support for
        non-sidereal targets in a future upgrade.
    
    ddec : float
        Dec differential tracking rate in arcsec/hr. This is the backwards
        compatible way of supporting non-sidereal targets.  We plan to add
        additional support for non-sidereal targets in a future upgrade.
    
    comment : string
        An arbitrary user comment.
    
    Acquisition Strategies
    ----------------------
    guider: bright
        Target will be visible on typical guider exposures.  No special
        exposure settings needed.
    
    guider: faint
        Target will need either increased exposure time (i.e. for visible light
        guide cameras) or will need sky subtraction (i.e. for IR guide cameras)
    
    guider: offset
        The target coordinates are for an offset star and offsets will be used
        to center the science target after centering the offset star.
    
    mask align
        Acquisition use the slitmask alignment tool.  Typically by imaging
        known alignment stars through alignment holes in the mask.
    
    blind
        Just point and shoot.
    
    Rotator Modes
    -------------
    PA
        The rotator will keep the instrument fixed in sky position angle (fixed
        relative to the celestial coordinates).
    
    stationary
        The rotator will be fixed in position relative to the instrument.  The
        sky may rotate around the target.
    
    vertical
        The rotator will keep the instrument fixed in horizon coordinates.  A
        position angle of 0 will mean the slit has the long axis parallel to
        elevation.
    
    Object Types
    ------------
    science
    sky
    flux standard
    telluric standard
    custom
    '''
    def __init__(self, name=None, RA=None, Dec=None, equinox=None, frame='icrs',
                 rotmode=None, PA=None, RAOffset=None, DecOffset=None,
                 objecttype=None, acquisition=None,
                 PMRA=0, PMDec=0, epoch=None, obstime=None,
                 mag = {'B': None, 'V': None, 'R': None, 'I': None,
                        'u': None, 'g': None, 'r': None, 'i': None, 'z': None,
                        'Y': None, 'J': None, 'H': None, 'K': None, 'Ks': None,
                        'L': None, 'M': None},
                wrap=None,
                dra=0, ddec=0,
                comment=None
                ):
        self.RA = RA
        self.Dec = Dec
        self.equinox = equinox
        # Optional
        self.rotmode = rotmode
        self.PA = PA
        self.RAOffset = RAOffset # in arcsec
        self.DecOffset = DecOffset # in arcsec
        self.objecttype = objecttype
        self.acquisition = acquisition
        self.mag = mag
        self.frame = frame
        self.PMRA = PMRA # proper motion in RA in arcsec per year
        self.PMDec = PMDec # proper motion in Dec in arcsec per year
        self.epoch = epoch # required if RAPM or DecPM is set
        self.obstime = obstime
        self.wrap = wrap
        self.dra = dra
        self.ddec = ddec
        self.comment = comment

        self.name = name
        if name is not None and RA is None and Dec is None:
            if name.lower() not in ['none', 'domeflat', 'domeflats']:
                # Try to get coordinates from the name
                self.from_name(name)
        else:
            if type(RA) == str and type(Dec) == str:
                sc = c.SkyCoord(f'{RA} {Dec}', unit=(u.hourangle, u.deg),
                                frame=self.frame)
                self.RA = sc.ra.deg
                self.Dec = sc.dec.deg
            else:
                self.RA = RA
                self.Dec = Dec
            if frame == 'icrs':
                self.equinox = 2000
            else:
                self.equinox = equinox

        self.location = c.EarthLocation.of_site('keck')
#         self.validate()


    ##-------------------------------------------------------------------------
    ## Validate
    ##-------------------------------------------------------------------------
    def validate(self):
        '''Check values on this object and verify that they meet assumptions.
        
        Check:
        - rotator mode is valid value
        - PA is 0-360 (may need different limits for other modes)
        - acquisition is valid value
        - type is valid value [Science, Sky, Flux standard, Telluric standard,
          Custom]
        
        Warn:
        - no rotator mode
        - rotator mode is PA and no PA set
        - rotator mode is vertical and PA != 0
        - acquisition not given
        '''

        if self.name is None:
            raise TargetError('name is required')
        if self.RA is None and self.name.lower() not in cal_positions:
            raise TargetError('RA is required')
        if self.Dec is None and self.name.lower() not in cal_positions:
            raise TargetError('Dec is required')
        if self.equinox is None and self.name.lower() not in cal_positions:
            raise TargetError('equinox is required')

        if self.rotmode is None:
            self.rotmode = 'PA'
            warn('No rotator mode given, assuming PA mode',
                          category=TargetWarning)
        if self.rotmode.lower() not in rotator_modes:
            raise TargetError(f'Rotator mode "{self.rotmode}" is not valid')
        if self.PA is None:
            self.PA = 0
            warn('No PA given, assuming 0 deg', category=TargetWarning)
        if self.PA < valid_PAs.get(self.rotmode.lower())[0]\
            or self.PA > valid_PAs.get(self.rotmode.lower())[1]:
            raise TargetError(f'Rotator PA "{self.PA:.1f}" not in range '
                              f'{valid_PAs.get(self.rotmode.lower())}')

        if self.acquisition is None:
            self.acquisition = 'guider: bright'
            warn('No acquisition mode given, assuming "guider: bright"',
                          category=TargetWarning)
        if self.acquisition.lower() not in acquisition_modes:
            raise TargetError(f'Acquisition mode "{self.acquisition}" not valid')

        if self.objecttype is None:
            self.objecttype = 'science'
            warn('No object type given, assuming "science"',
                          category=TargetWarning)
        if self.objecttype.lower() not in object_types:
            raise TargetError(f'Object type "{self.objecttype}" is not valid')

        if self.wrap is not None:
            if self.wrap.lower() not in telescope_wraps:
                raise TargetError(f'Wrap "{self.wrap}" is not valid')


    ##-------------------------------------------------------------------------
    ## Coordinate
    ##-------------------------------------------------------------------------
    def coord(self):
        '''Return an astropy.coordinates.SkyCoord object based on the RA & Dec.
        If both proper motion values and an epoch are given, propagate the
        coordinate forward in time from the epoch to now based on those proper
        motions.
        '''
        # Reminder: equinox is the precession equinox in which the coordinate
        #           is specified (e.g. 1950 or 2000).
        myequinox = Time(self.equinox, format='decimalyear', scale='utc')
        # Reminder: epoch is the time at which the coordinate is defined. If
        #           the observation time is not the same as the epoch, then
        #           proper motion will have to be factored in to get an updated
        #           coordinate.
        myepoch = Time(self.epoch, format='decimalyear', scale='utc')\
                  if self.epoch is not None else Time.now()
        sc = c.SkyCoord(self.RA*u.deg, self.Dec*u.deg, frame=self.frame,
                        equinox=myequinox,
                        obstime=myepoch,
                        pm_ra_cosdec=self.PMRA*u.arcsec/u.yr,
                        pm_dec=self.PMDec*u.arcsec/u.yr,
                        distance=1*u.kpc, # distance is for apply_space_motion
                       )
        if abs(self.PMRA) > 0 and abs(self.PMDec) > 0:
            if self.obstime is None:
                obstime = Time.now()
            elif type(self.obstime) == Time:
                obstime = self.obstime
            else:
                obstime = Time(self.obstime, format='decimalyear', scale='utc')
            return sc.apply_space_motion(new_obstime=obstime)
        else:
            return sc


    def altaz(self):
        '''Return the AltAz frame coordinate of the target.
        '''
        obstime = Time.now() if self.obstime is None else self.obstime
        altazframe = c.AltAz(location=self.location, obstime=obstime)
        return self.coord().transform_to(altazframe)


    def alt(self):
        '''Return the altitude of the target in degrees.
        '''
        return self.altaz().alt


    def az(self):
        '''Return the azimuth of the target in degrees.
        '''
        return self.altaz().az


    def moon_separation(self):
        '''Return the separation in degrees of the target from the Moon or
        return None if the Moon is not above the horizon.
        '''
        obstime = Time.now() if self.obstime is None else self.obstime
        moon = c.get_moon(obstime, location=self.location)
        altazframe = c.AltAz(location=self.location, obstime=obstime)
        moon_alt = ((moon.transform_to(altazframe).alt).to(u.degree)).value
        if moon_alt < 0:
            return None
        return self.coord().separation(moon).to(u.degree)


    ##-------------------------------------------------------------------------
    ## From Name
    ##-------------------------------------------------------------------------
    def from_name(self, name):
        '''Get the coordinate using the from_name SkyCoord method.
        '''
        sc = c.SkyCoord.from_name(name)
        self.name = name
        self.RA = sc.ra.deg
        self.Dec = sc.dec.deg
        self.frame = sc.frame.name
        if sc.frame.name == 'icrs':
            self.equinox = 2000


    ##-------------------------------------------------------------------------
    ## Output a star list line
    ##-------------------------------------------------------------------------
    def to_starlist(self):
        '''Return string corresponding to a traditional Keck star list entry.
        '''
        coord = self.coord()
        coord_str = coord.to_string('hmsdms', sep=' ', precision=2)
        line = f"{self.name:16s} {coord_str} {self.equinox}"
        if self.rotmode is not None: line += f' rotmode={self.rotmode}'
        if self.PA is not None: line += f' PA={self.PA:.1f}'
        if self.RAOffset is not None: line += f' raoff={self.RAOffset}'
        if self.DecOffset is not None: line += f' decoff={self.DecOffset}'
        if self.wrap is not None: line += f' wrap={self.wrap}'
        if 'V' in self.mag.keys():
            if self.mag['V'] is not None:
                # Use lowercase v convention from starlist
                # This is the only magnitude in the starlist specification
                line += f' vmag={self.mag["V"]:.2f}'
        if abs(self.dra) > 0: line += f' dra={self.dra}'
        if abs(self.ddec) > 0: line += f' ddec={self.ddec}'
        # Now add comments
        line += ' #'
        for filt in self.mag.keys():
            if self.mag[filt] is not None:
                line += f' {filt}mag={self.mag[filt]:.2f}'
        if self.comment is not None: line += f' {self.comment}'
        return line


    ##-------------------------------------------------------------------------
    ## Output a TDL yaml snippet
    ##-------------------------------------------------------------------------
    def to_dict(self):
        '''Return dictionary corresponding to a Target Description Language
        (TDL) entry.
        '''
        coord = self.coord()
        mags = dict()
        for band in self.mag.keys():
            if self.mag.get(band, None) is not None:
                mags[band] = self.mag.get(band)
        # Convert obstime
        if self.obstime is None:
            obstime = self.obstime
        elif type(self.obstime) in [float, int]:
            obstime = self.obstime
        elif type(self.obstime) == Time:
            obstime = float(self.obstime.to_value('decimalyear'))

        TDL_dict = {
            'name': self.name,
            'RA': float(coord.ra.deg),
            'Dec': float(coord.dec.deg),
            'equinox': float(coord.equinox.byear),
            'epoch': float(coord.obstime.byear),
            'frame': coord.frame.name,
            'rotmode': self.rotmode,
            'PA': self.PA,
            'RAOffset': self.RAOffset,
            'DecOffset': self.DecOffset,
            'objecttype': self.objecttype,
            'acquisition': self.acquisition,
            'PMRA': self.PMRA,
            'PMDec': self.PMDec,
            'obstime': obstime,
            'mag': mags,
            'wrap': self.wrap,
            'dra': self.dra,
            'ddec': self.ddec,
            'comment': self.comment,
        }
        return TDL_dict


    def write(self, file):
        tl = TargetList([self])
        tl.write(file)


    def __str__(self):
        return f"{self.name}"


    def __repr__(self):
        return self.to_starlist()


##-------------------------------------------------------------------------
## TargetList
##-------------------------------------------------------------------------
class TargetList(UserList):
    '''An object to hold a list of Target objects.
    '''
    def validate(self):
        '''Run the validate method on all Targets in the list.
        '''
        for t in self.data:
            t.validate()


    def set_obstime(self, obstime):
        '''Set obstime to the given value for all targets in the list.
        '''
        if type(obstime) == Time:
            pass
        else:
            obstime = Time(obstime, format='decimalyear', scale='utc')
        for i,t in enumerate(self.data):
            self.data[i].obstime = obstime


    def to_dict(self):
        # self.validate()
        return {'Targets': [t.to_dict() for t in self.data]}


    def write(self, file):
        '''Write the target list to a YAML formatted file.
        '''
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(yaml.dump([self.to_dict()]))


    def parse_yaml(self, contents):
        list_of_dicts = contents[0]['Targets']
        targets = [Target(name=d.get('name', None),
                          RA=d.get('RA', None),
                          Dec=d.get('Dec', None),
                          equinox=d.get('equinox', None),
                          rotmode=d.get('rotmode', None),
                          PA=d.get('PA', None),
                          RAOffset=d.get('RAOffset', None),
                          DecOffset=d.get('DecOffset', None),
                          objecttype=d.get('objecttype', None),
                          acquisition=d.get('acquisition', None),
                          frame=d.get('frame', None),
                          PMRA=d.get('PMRA', 0),
                          PMDec=d.get('PMDec', 0),
                          epoch=d.get('epoch', None),
                          obstime=d.get('obstime', None),
                          mag = d.get('mag', {}),
                          comment=d.get('comment', None),)\
                   for d in list_of_dicts]
        return TargetList(targets)


    def read(self, file):
        '''Read targets from a YAML formatted file.
        '''
        p = Path(file).expanduser().absolute()
        if p.exists() is False:
            raise FileNotFoundError
        with open(p, 'r') as FO:
            contents = yaml.safe_load(FO)
        return self.parse_yaml(contents)


    def to_starlist(self):
        '''Return a string representation of the Targets which matches the
        formatting specification of a Keck star list.
        '''
#         self.validate()
        starlist_str = ''
        for t in self.data:
            starlist_str += t.to_starlist() + '\n'
        return starlist_str


    def write_starlist(self, file):
        '''Write the target list to a Keck star list formatted file.
        '''
#         self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            for t in self.data:
                FO.write(t.to_starlist() + '\n')


    def __str__(self):
        return self.name


    def __repr__(self):
        return self.to_starlist()


##-------------------------------------------------------------------------
## Pre-Defined Targets
##-------------------------------------------------------------------------
def DomeFlats(PA=0):
    '''Function to return a Target for dome flats
    '''
    return Target(name='DomeFlats', rotmode='Stationary', PA=PA,
                  objecttype='cal', acquisition='blind')
