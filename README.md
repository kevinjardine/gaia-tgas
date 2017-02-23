This is code to extract isosurface density meshes and related data from the TGAS (Tycho-Gaia Astrometric Solution) dataset from [Gaia DR1](https://www.cosmos.esa.int/web/gaia/dr1).

It uses several Python libraries, including the standard numpy, scipy and matplotlib libraries as well as the Visual Toolkit (vtk) 7.0 library to actually extract and manipulate the isosurfaces using the marching cubes algorithm and the Blender 2.78 embedded Python interpreter to render images.

There seems to be limited working code available for the Blender interpreter and (especially) the vtk library so by releasing this code I hope to encourage scientists to take more advantage of the amazing power of these libraries to visualize large data sets.

## Scripts

*tgas_make_star_list.py*

This generates a star list csv file used by the other scripts. It combines colour index data extracted from the Hipparcos and Tycho catalogs with magnitude, parallax and position data from TGAS. It sets hot star flags (colour index < 0) and bright star flags (absolute magnitude < 3) for use in constructing the isosurfaces. The stars in the resulting list all have low parallax errors with positive parallaxes and err/parallax < 0.2.

*tgas_make_slices.py*

Given the isosurface type (hot or bright) as an argument, this script produces two directories of density slices. The TGAS data fades out after a radius of 800 parsecs, and this code accumulates a star count of either hot or bright stars in bins of size 2x2x2 parsecs. One directory (cm) is just colour mapped slices for visual inspection. The second (16bit) directory is used as input for the next script to generate isosurfaces.

*tgas_make_isosurfaces.py*

Given the isosurface type (hot or bright) as an argument, this script generates density isosurfaces from the density slices produced in the previous script. In addition, the script produces:

- filtered isosurfaces such that each distinct region within the filtered isosurface contains five or more (hot or bright) stars
- csv files that list each star in an isosurface broken down by region (in the final column)
- csv files that summaries the low error, hot and bright star count in each isosurface region

*tgas_region_structure.py*

Given the isosurface type (hot or bright) as an argument, this script generates a text file that summarizes the isosurface structures, showing which isosurface region sits inside another.

*tgas_blender_ortho.py* and *tgas_blender_pan.py*

If you feed these scripts to your Blender executable with an isosurface type (hot or bright) as an argument, they will generate either orthographic images of isosurfaces from above the galactic plane (tgas_blender_ortho.py) or panoramic images from the position of the Sun (tgas_blender_pan.py).

Example:

blender --background --python tgas_blender_ortho.py -- hot

In addition, the code will generate a shell script that if run will create an image that stacks the isosurfaces to create an image that looks a little like a mountain range, showing the regions of maximum star density.

*tgas_svg_ortho.py* and *tgas_svg_pan.py*

Given an isosurface type (hot or bright) as an argument, these scripts will combine images and isosurface structure data together to generate either annotated orthographic svg images of isosurfaces from above the galactic plane (tgas_blender_ortho.py) or annotated panoramic svg images from the position of the Sun (tgas_blender_pan.py).

## License

This code is released into the public domain. Feel free to use it freely.