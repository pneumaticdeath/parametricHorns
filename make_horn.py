#!/usr/bin/env python
# Based on horn3.py by Tom P. (user tpchuckles on thingiverse.com)
# the original code can be found here: https://www.thingiverse.com/thing:5392373/files
# Modified by Mitch Patenaude (mitch@mitchpatenaude.net user pneumaticdeath on thingiverse.com)

from solid import * #SolidPython https://github.com/SolidCode/SolidPython
from solid.utils import *
import numpy as np

import argparse

default_output="horn.scad"

# d=25; D=35 ; H=100 ; nribs=10 ; nrots=2 ; N=200 ; n=20 ; ntwists=3

parser = argparse.ArgumentParser('make_horn.py')
parser.add_argument('-d', '--spiral-diameter', type=float, default=25.0, help="base diameter of the spiral going up the suface of the cone (default 25)")
parser.add_argument('-D', '--cone-diameter', type=float, default=35.0, help='base diameter of the cone (default 35)')
parser.add_argument('-H', '--height', type=float, default=100.0, help='height of the cone (default 100)')
parser.add_argument('-r', '--ribs', type=int, default=10, help='number of ribs per rotation (default 10)')
parser.add_argument('-R', '--rotations', type=int, default=2, help='rotations around the cone (default 2)')
parser.add_argument('-N', '--layers', type=int, default=200, help='(default 200)')
parser.add_argument('-n', '--spirals', type=int, default=20, help='(default 20)')
parser.add_argument('-t', '--twists', type=float, default=3.0, help='(default 3)')
parser.add_argument('--output', type=str, default=default_output)

args = parser.parse_args()

# CONE
# a horn spirals up the surface of a cone, twisting along the way
# definition of a cone: r=R/H*(z-H) # simply y-y0=m*(x-x0) where slope is -R/H, and (x0,y0) is (H,0)
R=args.cone_diameter/2 ; zs=np.linspace(-args.spiral_diameter/2, args.height, args.layers) ; radii=R/args.height*(zs-args.height)

# SPIRAL ON CONE
# spiralling up a cone, we know r, h, and just need theta, and we've got each point defined in cylindrical coords
thetas=np.linspace(0, 2*np.pi*args.rotations, args.layers)
path=[ [ r*np.sin(t) , r*np.cos(t) , z ] for r,t,z in zip(radii,thetas,zs) ] # why as a list comprehension? solidpython still seems to struggle with numpy arrays


# CROSS-SECTION: RIBBED CIRCLE
# ribs are semicircles placed around an underlying circle. radius of rib comes from arc length on this underlying circle. note that we want d to be the total diameter, with ribs! say d_circ is underlying circle diameter, d_rib=(d_circ/2)*pi*2/nribs, d_tot=d_circ+d_rib
d_circ=args.spiral_diameter/(1+(1/2)*pi*2/args.ribs) ; d_rib=(d_circ/2)*pi*2/args.ribs
# radius of rib comes from arc length on this underlying circle. also calculate angle to the center of each rib
thetas=np.linspace(0,2*np.pi, args.ribs, endpoint=False)
centers=np.asarray([d_circ/2*np.sin(thetas) , d_circ/2*np.cos(thetas) ] ) # x,y coordinates of each rib center
profile=[]
for x,y,t in zip(*centers,thetas):
	for a in np.linspace(t-np.pi,t+np.pi, 30, endpoint=False): # angle range? not 0-2*pi! t is "straight out" on rib, so -/+pi
		px , py = x+d_rib/2*np.sin(a) , y+d_rib/2*np.cos(a)
		if ( px**2+py**2 )**(1/2) < d_circ/2:
			continue
		profile.append([px,py])

# SCALING AND ROTATION
scaling=list(np.linspace(1,.01,args.layers))
rots=[args.twists*360] # https://github.com/SolidCode/SolidPython/blob/master/solid/extrude_along_path.py
#thetas=list(np.linspace(0,2*np.pi*ntwists,N))

# EXTRUDE ALONG PATH
extruded=extrude_along_path(shape_pts=profile,path_pts=path,scales=scaling,rotations=rots)

# TOUCH-UPS
extruded+=translate(path[-1])(sphere((args.spiral_diameter)/2*scaling[-1])) # a sphere gives us a rounded tip for the horn
crop_size = max(args.height, args.cone_diameter)
extruded-=translate([-crop_size,-crop_size,-2*crop_size])(cube([2*crop_size, 2*crop_size, 2*crop_size]))# flatten the bottom

openscadCode="$fn=100;"
openscadCode=openscadCode+scad_render(extruded)
outFile=open(args.output,"w")
outFile.write(openscadCode)
outFile.close()
