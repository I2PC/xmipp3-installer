CMAKE_LIB_VERSIONS = """CMake=3.28.3
CC=GNU-13.2.0
CXX=GNU-13.2.0
Python3=3.8.19
CUDA=12.2.91
MPI=3.1
HDF5=1.10.10
JPEG=80
SQLite3=3.45.3
Java=21.0.5
"""

LOG_TAIL_ERROR = """[ 45%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/resolution_localfilter.cpp.o
[ 45%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/resolution_monogenic_signal.cpp.o
[ 45%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/resolution_pdb_bfactor.cpp.o
[ 45%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/shift_corr_estimator.cpp.o
[ 45%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/single_extrema_finder.cpp.o
[ 45%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/subtomo_subtraction.cpp.o
[ 46%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/subtract_projection.cpp.o
[ 46%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/symmetrize.cpp.o
/home/runner/work/xmipp/xmipp/src/xmipp/libraries/reconstruction/subtract_projection.cpp: In member function ‘void ProgSubtractProjection::writeParticle(MDRow&, FileName, Image<double>&, double, double, double, double, double, double, double)’:
/home/runner/work/xmipp/xmipp/src/xmipp/libraries/reconstruction/subtract_projection.cpp:161:25: error: ‘MDL_SUBTRACTION_B’ was not declared in this scope; did you mean ‘MDL_SUBTRACTION_R2’?
  161 |         rowOut.setValue(MDL_SUBTRACTION_B, b);
      |                         ^~~~~~~~~~~~~~~~~
      |                         MDL_SUBTRACTION_R2
[ 46%] Building CXX object src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/threshold.cpp.o
gmake[2]: *** [src/xmipp/CMakeFiles/Xmipp.dir/build.make:3394: src/xmipp/CMakeFiles/Xmipp.dir/libraries/reconstruction/subtract_projection.cpp.o] Error 1
gmake[2]: *** Waiting for unfinished jobs....
gmake[1]: *** [CMakeFiles/Makefile2:1794: src/xmipp/CMakeFiles/Xmipp.dir/all] Error 2
gmake: *** [Makefile:166: all] Error 2


Error 5: Error compiling with CMake.
Check the inside file 'compilation.log'. 
More details on the Xmipp documentation portal: https://i2pc.github.io/docs/
Error: Process completed with exit code 1."""

LOG_TAIL_SUCCES = """-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/histogram.png
-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/delete.gif
-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/create_selection.png
-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/export_wiz.gif
-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/linearPickingC.png
-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/step_finished.gif
-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/tree.gif
-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/freehand.png
-- Installing: /home/runner/work/xmipp/xmipp/dist/resources/invert_selection.png
-- Installing: /home/runner/work/xmipp/xmipp/dist/bin/xmipp_metadata_plot
-- Installing: /home/runner/work/xmipp/xmipp/dist/bin/xmipp_showj
-- Installing: /home/runner/work/xmipp/xmipp/dist/./xmipp.bashrc
Done

******************************************************************
*                                                                *
*     Xmipp devel has been successfully installed, enjoy it!     *
*                                                                *
******************************************************************"""
