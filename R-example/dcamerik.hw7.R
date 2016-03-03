#For Problem 1:
#Import the LAI data
library(fields)
LAIdata<-read.table('LAI.csv',sep=',')
LAIdata<-as.matrix(LAIdata)
maxt<-dim(LAIdata)[1]
LAI<-sapply(1:maxt,function(i) matrix(LAIdata[i,],nrow=120,ncol=60,byrow=T),simplify="array")

#Obtain the LAI data for the first timepoint to use for the rest of this code
LAI1 = LAI[,,1]

#This will sample from the land only, so get all of the points on the land
naland = which(LAI1!=0,arr.ind=T)

#Use a sequence of n values, from 10 to 200 with increments of 10
nvals = seq(10,200,by=10)

accLAIestim = numeric(length(nvals))
#Sample points on the land for each sample size
for (i in 1:length(nvals))
{
  if (i > 1)
  {
    print(accLAIestim[i-1])
  }
  sumLAI = 0
  nval = nvals[i]
  landsample = sample(1:dim(naland)[1],size=nval,replace=FALSE)
  for (i in 1:nval)
  {
    sumLAI = sumLAI+LAI1[naland[landsample[i],1],naland[landsample[i],2]]
  }
  accLAIestim[i] = sumLAI*as.numeric(dim(naland)[1]/nval)*12
  print(accLAIestim[i])
}
#This screws up somehow when restarting the loop so that some of the accLAIestim values become either 0 or NA (and they increase to 200), so they must be fixed
newaccLAIestim = accLAIestim[complete.cases(accLAIestim)]
include = which(newaccLAIestim>0)
newnewaccLAIestim = newaccLAIestim[include]
#The remaining values are the estimated sums

#Get the actual accumulated LAI for 2005 (which will be used to plot)
accLAI = 0
for (i in 1:12)
{
  accLAI = accLAI+sum(colSums(LAI[,,i]))
}

#Get the MC errors, which will be the absolute value of the true value minus the estimated value
MCerror = numeric(length(newnewaccLAIestim))
for (i in 1:length(newnewaccLAIestim))
{
  MCerror[i] = abs(accLAI-newnewaccLAIestim[i])
}

#Plot the estimates and errors
plot(nvals,newnewaccLAIestim,type='l',xlab='Sample size',ylab='MC estimate',main='Plot of MC estimates for 2005 Acc LAI')
plot(nvals,MCerror,type='l',xlab='Sample size',ylab='MC error',main='Plot of MC errors for 2005 Acc LAI')

#For Problem 2:
#For part (b):
#Define the h functions for the Gaussian and gamma algorithms
hfungauss = function(x)
{
  return((sin(x)^2)*x^2*exp((-(x^2))/2))
}

hfungamma = function(x)
{
  return(gamma(x)*exp(x)*(sin(x)^2)*exp((-(x^2))/2))
}

#Get the Monte Carlo estimate, error, and 95% confidence interval for the Gaussian algorithm
nSple = 10000
Gaussians = rnorm(n=nSple,mean=0,sd=1)
hvaluesgauss = hfungauss(Gaussians)
Ihatgauss = mean(hvaluesgauss) #Monte Carlo estimate: an estimate found is 0.2422932
segauss = sqrt(var(hvaluesgauss)/nSple) #Monte Carlo error: for the above Ihat, error is 0.00258659
zgauss = qnorm(0.975)
CIgauss = c(Ihatgauss-zgauss*segauss,Ihatgauss+zgauss*segauss) #95% confidence interval
#For the above Ihat, se, and z, the confidence interval is (0.2372236, 0.2473628)

#Get the Monte Carlo estimate, error, and 95% confidence interval for the gamma algorithm
gammas = rgamma(n=nSple,shape=3,rate=1)
hvaluesgamma = hfungamma(gammas)
Ihatgamma = mean(hvaluesgamma) #Monte Carlo estimate: an estimate found is 0.4409859
segamma = sqrt(var(hvaluesgamma)/nSple) #Monte Carlo error: for the above Ihat, error is 0.004935336
zgamma = qnorm(0.975)
CIgamma = c(Ihatgamma-zgamma*segamma,Ihatgamma+zgamma*segamma) #95% confidence interval
#For the above Ihat, se, and z, the confidence interval is (0.4313128, 0.4506589)

#Plot the Monte Carlo errors for n=10,25,50,100,200,500,1000,5000,10000
nvals = seq(100,5000,by=100)
errorsgauss = numeric(length(nvals))
errorsgamma = numeric(length(nvals))
#Get the errors for each algorithm using the above sample sizes
for (i in 1:length(nvals))
{
  Gaussians = rnorm(n=nvals[i],mean=0,sd=1)
  hvaluesgauss = hfungauss(Gaussians)
  Ihatgauss = mean(hvaluesgauss)
  segauss = sqrt(var(hvaluesgauss)/nSple)
  errorsgauss[i] = segauss
  
  gammas = rgamma(n=nvals[i],shape=3,scale=1)
  hvaluesgamma = hfungamma(gammas)
  Ihatgamma = mean(hvaluesgamma)
  segamma = sqrt(var(hvaluesgamma)/nSple)
  errorsgamma[i] = segamma
}
#The errors for the Gaussian algorithm are a bit smaller than the errors for the gamma distribution
plot(nvals,errorsgauss,ylim=c(0,0.006),xlab="Sample size",ylab="Monte Carlo error",main="Monte Carlo errors for Gaussian algorithm",type='l')
plot(nvals,errorsgamma,ylim=c(0,0.006),xlab="Sample size",ylab="Monte Carlo error",main="Monte Carlo errors for Gamma algorithm",type='l')

#For part (c):
#Define the omega function
omegafunc = function(x)
{
  return((2/0.2422932)*(sin(x))^2*exp((-(x^2)/2)+x))
}

Y = rgamma(max(nvals),shape=3,rate=1)
Yminus1sq = (Y-1)^2
Y_ind = (1<Y)*(Y<10)
omega_Y = omegafunc(Y)
z = qnorm(0.975)
ResI = array(0,c(length(nvals),4))
for (i in 1:length(nvals))
{
  subspl = Y_ind[1:nvals[i]]*omega_Y[1:nvals[i]]*Yminus1sq[1:nvals[i]]
  m = mean(subspl)
  MC_error = sqrt(var(subspl)/nvals[i])
  lb = m-MC_error*z
  ub = m+MC_error*z
  ResI[i,] = c(m,lb,ub,MC_error)
}
