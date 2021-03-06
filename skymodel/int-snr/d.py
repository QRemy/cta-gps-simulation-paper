	
import os
from numpy import *
from astropy.table import Table
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy import wcs
from astropy.io import fits
import matplotlib.pyplot as plt
import naima

def prob(M, p0=0., a=0., m0=1e4):
    P=p0*(M/m0)**a
    return P


def snrmap(ra,dec,radius,outfile=''):
    xx=tile(arange(-1,1,0.01).reshape(200,1),[1,200])
    yy=tile(arange(-1,1,0.01).reshape(1,200),[200,1])
    zz2=(radius**2. -xx**2. -yy**2.)
    zz= sqrt(zz2*(zz2 > 0.))
    zz=zz/sum(zz)
    w = wcs.WCS(naxis=2)
    w.wcs.crpix = [101, 101]
    w.wcs.cdelt = [-0.01, 0.01]
    w.wcs.crval = [ra, dec]
    w.wcs.ctype = ["RA---AIT", "DEC--AIT"]
    h = w.to_header()
    hdu = fits.PrimaryHDU(header=h)
    hdu.data=zz
    hdu.writeto(outfile,overwrite=True)
    return zz



def createXml(srcname='source0',specfile='specfile.txt', mapfile='mapfile.fits'):
  code=[
  '   <source name="source0" type="DiffuseSource"  tscalc="1">\n',
  '       <spectrum file="model0.txt" type="FileFunction">\n',
  '           <parameter free="0" max="1000.0" min="0.0" name="Normalization" scale="1.0" value="1.0" />\n',
  '       </spectrum>\n',
  '       <spatialModel type="DiffuseMap" file="skymap0.fits">\n',
  '           <parameter name="Prefactor" value="1" scale="1" min="0.001" max="1000" free="0" />\n',
  '       </spatialModel>\n',
  '   </source>\n' ]


  code[0] = code[0].replace('source0',srcname)  
  code[1] = code[1].replace('model0.txt',specfile)
  code[4] = code[4].replace('skymap0.fits',mapfile)

  return code



def createXml_disk(srcname='source0',specfile='specfile.txt',lon=0.0,lat=0.0,radius=1.0):
  code=[
  '   <source name="source0" type="ExtendedSource""  tscalc="1">\n',
  '       <spectrum file="model0.txt" type="FileFunction">\n',
  '           <parameter free="0" max="1000.0" min="0.0" name="Normalization" scale="1.0" value="1.0" />\n',
  '       </spectrum>\n',
  '      <spatialModel type="RadialDisk">\n',
  ' 		 <parameter name="GLON"    scale="1.0" value="888" min="-360" max="360" free="0"/>\n',
  ' 		 <parameter name="GLAT"   scale="1.0" value="777" min="-90"  max="90"  free="0"/>\n',
  '  	 	 <parameter name="Radius" scale="1.0" value="111"    min="0.005" max="10"  free="1"/>\n',
  '	</spatialModel>\n',  
   '   </source>\n' ]


  code[0] = code[0].replace('source0',srcname)  
  code[1] = code[1].replace('model0.txt',specfile)
  code[5] = code[5].replace('888',str(lon))
  code[6] = code[6].replace('777',str(lat))
  code[7] = code[7].replace('111',str(radius))

  return code



####### Input

database_snr='../snr/OUTPUT_FILES_1/ctadc_skymodel_gps_sources_pevatron_0.ecsv'
#database_snr='../snr/ALL_FILES_0/results_0.txt'

database_nubi='Clouds.fits'

threshold = 0.    # threshold for flux 

# Prob params

alpha=0 ; p0=0.015


#### Output dir

#path=str(int(random.random(1)*1e5))

path='out/'
os.system('rm -r '+path)
os.system('mkdir '+path)



#### Energy channels

energy_b = logspace(8,14.4,101)*u.eV
de = energy_b[1:]-energy_b[:-1]
energy = sqrt(energy_b[1:]*energy_b[:-1])

### XML init

code=[
'<?xml version="1.0" standalone="no"?>\n',
'<source_library title="interacting supernova remnants">\n'
]


######  Mol. Clouds

cloud=Table.read(database_nubi)

pp=prob(cloud['Mass'], p0=p0, a=alpha)
rand=random.random(len(cloud))
is_int = (rand < pp)*(cloud['Mass'].data > 3e3)
true_index=is_int.nonzero()
w=true_index[0]                     # Indeces of iSNR random select from synthetic catalog
n_isnr = len(w) 

#### SNRs

try : 

 snr=Table.read(database_snr,format='ascii.ecsv')
 
except:

  q = Table.read(database_snr, format='ascii')
  step = 40
  n_snr = len(q)/step
  snr=q[arange(n_snr).astype(int)*step]

  gpos = SkyCoord( snr['POS_X'].data*u.kpc, snr['POS_Y'].data*u.kpc, snr['POS_Z'].data*u.kpc, frame='galactocentric',galcen_distance=8.5*u.kpc)  

  snr['glon'] = gpos.galactic.l
  snr['glat'] = gpos.galactic.b 
  snr['distance'] = gpos.galactic.distance
  
  snr['sigma'] = snr['size'] * u.arcmin
  snr['agekyr'] = snr['age[kyr]'] * u.kyr
  

#snr['id']=arange(len(snr))

w_cc =  where((snr['agekyr'] < 40 ) & (snr['type'] != 1))   
ncc = len(w_cc[0])
          

# List of iSNRs


icloud=cloud[w]
icloud['Flux_int_100GeV']=icloud['Flux_int_100MeV']*0.
icloud['Flux_int_1TeV']=icloud['Flux_int_100MeV']*0.
icloud['Flux_int_10TeV']=icloud['Flux_int_100MeV']*0.
icloud['Cloud_id'] = w

isnr = w_cc[0][(random.random(n_isnr)*ncc).astype(int)] # indices of snr which corrspoonds to iSNRs
icloud['SNR_id'] = isnr

icloud['Distance'] = snr['distance'][isnr]

#rho = 10*u.pc / icloud['Distance'].quantity.to('pc') * u.rad
rho = snr['sigma'][isnr].quantity 
costheta = random.random(n_isnr) 
phi      = random.random(n_isnr) *2*pi
xsep = rho*arccos(costheta)*cos(phi)
ysep = rho*arccos(costheta)*sin(phi) 

icloud['Glat'] = snr['glat'][isnr] + ysep
icloud['Glon'] = snr['glon'][isnr] + xsep


for i in arange(len(icloud)):
#for i in arange(10):

  print('Source ',i+1)
  #print('Luminosity',icloud['Luminosity'][i],'Flux_int_100MeV',icloud['Flux_int_100MeV'][i])
  
  ind1 = icloud['index1'][i]
  ind2 = icloud['index2'][i]
  ebreak  = icloud['Energy_break'][i]
  #dist = icloud['Distance'][i]*u.cm               # cm
  dens = icloud['Density'][i] * u.cm**-3.          # H / cm3
  mass = icloud['Mass'][i]*u.solMass               # Sol masses
  vol  = mass.to_value('u') / dens                 # cm3    
  radi = ( vol*3/(4.*pi) )**(1./3.)                # cm
  
  isnr = w_cc[0][int(random.random(1)*ncc)]

  lat = icloud['Glat'][i]  *u.deg
  lon = icloud['Glon'][i]  *u.deg
  dist = icloud['Distance'][i] *u.kpc
  gpos = SkyCoord(l=lon, b=lat, frame='galactic')
  #radi = snr['sigma'][isnr]/2. *u.arcmin 

  radius = radi / dist.to('cm') * u.rad

  #print (radius.to('deg'), dens )

  epsilon=30. *u.cm**(-3)*u.eV
  #epsilon= icloud['Epsilon'][i]

  E0=1e12*u.eV
  A=1/u.TeV
  
  PL=naima.models.BrokenPowerLaw(A,E0,ebreak*u.MeV,ind1,ind2)
  PD=naima.models.PionDecay(PL,nh=dens,nuclear_enhancement=True)
  
  wp=vol*epsilon       # tot. energy in protons [eV]
  PD.set_Wp(wp)
  
  lum = PD.flux(energy, distance = 0.)
  
  flux=PD.flux(energy, distance = dist)    # ph / cm2 s eV
  sed =PD.sed( energy, distance = dist)
 
  intLum        = sum( lum*de *energy.to('erg'))
  intFlux100MeV = sum(flux*de *energy.to('erg') *(energy > 100e6*u.eV)  )
  intFlux100GeV = sum(flux*de *energy.to('erg') *(energy > 100e9*u.eV)  )
  intFlux1TeV   = sum(flux*de *energy.to('erg') *(energy >  1e12*u.eV)  )
  intFlux10TeV  = sum(flux*de *energy.to('erg') *(energy > 10e12*u.eV)  )

  icloud['Flux_int_100MeV'][i] = intFlux100MeV.value
  icloud['Flux_int_100GeV'][i] = intFlux100GeV.value
  icloud['Flux_int_1TeV'][i]   = intFlux1TeV.value
  icloud['Flux_int_10TeV'][i]  = intFlux10TeV.value
 
  print('Luminosity :',intLum, '    Flux (>100GeV) :',intFlux100GeV )
  #print('ph / cm2 s',sum(flux *de))   


  if intFlux100GeV.to_value('erg / (cm2 s)') > threshold : 

    print('  --> added to the skymodel')

    #plt.plot(energy,sed)
  
    #specfile=path+'/isnr'+ str(i)+'_spec.txt'
    specfile='isnr'+ str(i)+'_spec.txt'
    spectrum=Table()
    spectrum['Energy']=energy.to('MeV') 
    spectrum['Flux']=flux.to('1 / (cm2 MeV s)')         
    spectrum.write(path+specfile,format='ascii.no_header',overwrite=True)

    # Map
    #mapfile=path+'/skymap'+str(i)+'.fits'
    #pippo=snrmap(gpos.icrs.ra.value, gpos.icrs.dec.value, radius.to_value('deg'), outfile=mapfile)
    #code=code+createXml(srcname='isnr'+str(i),specfile=specfile, mapfile=mapfile)

    # Disk 
    code=code+createXml_disk(srcname='isnr'+str(i),specfile=specfile, lon=lon.to_value('deg'), lat=lat.to_value('deg'),radius=min(max(radius.to_value('deg'),0.005),10.)) 


code=code+['</source_library>/n']

outfile = path+'/isnr.xml'
print ('Writing file : '+outfile)
mod = open(outfile, 'w')
mod.writelines(code)
mod.close()
       
#plt.loglog()
#plt.show()
    
icloud.write(path+'/d.fits',format='fits',overwrite=True)

    

