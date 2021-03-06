PKG_NAME=pcmdi_metrics
USER=PCMDI
OS=linux-64

mkdir ~/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=~/conda-bld
export VERSION=`date +%Y.%m.%d`


mkdir ~/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=~/conda-bld
export VERSION=`date +%Y.%m.%d`
conda build .
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION-0.tar.bz2 --force

mv meta.yaml meta-no-nox.yaml
mv meta-nox.yaml meta.yaml
conda build .
mv meta.yaml meta-nox.yaml
mv meta-no-nox.yaml meta.yaml
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-nox-$VERSION-0.tar.bz2 --force

