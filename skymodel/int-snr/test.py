import gammalib

xmlfile='out/isnr.xml'

try:
  q=gammalib.GModels(xmlfile)
  mss='  '+xmlfile+' loaded!'
  print(mss)
  
except:
  mss='  '+'problem in loading '+ xmlfile
  print(mss)
  