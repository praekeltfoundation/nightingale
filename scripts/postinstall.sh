manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

if [ ! -f ${INSTALLDIR}/nightingale-installed ]; then
    su - postgres -c "createdb nightingale"
    su - postgres -c "psql nightingale -c 'CREATE EXTENSION hstore; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;'"

    mkdir ${INSTALLDIR}/${REPO}/nightingale/static

    chown -R ubuntu:ubuntu ${INSTALLDIR}/${REPO}/media
    chown -R ubuntu:ubuntu ${INSTALLDIR}/${REPO}/static

    $manage syncdb --noinput
    $manage collectstatic --noinput
    touch ${INSTALLDIR}/nightingale-installed
else
    $manage migrate --noinput
    $manage collectstatic --noinput
fi