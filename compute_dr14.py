from numpy  import *
import math


def dr_rms( y ) 
	n = y.shape
	rms = numpy.sqrt( 2 * sum( y , 0 ) / n[0] ) 
	return rms 
	
def u_rms( y ) 
	n = y.shape
	rms = numpy.sqrt( sum( y , 0 ) / n[0] ) 
	return rms 

def decibel_u( y , ref )
	20*numpy.log10( ref / y )

def compute_dr14( Y , Fs )
	s = Y.shape
	ch = s[1]
	
	block_time = 3 
	cut_best_bins = 0.2
	block_samples = block_time * FS
	
	seg_cnt = math.floor( s[0] / block_samples )
	
	if seg_cnt < 3:
		return ( 0 , -100 , -100 )
	
	curr_sam = 0 
	rms = zeros((seg_cnt,ch))
	peaks = zeros((seg_cnt,ch))
	
	for i in range(seg_cnt):
		r = arange(curr_sam,curr_sam+block_samples)
		rms[i,:] = dr_rms( Y[r,:] ) 
		p = numpy.max( numpy.abs( Y[r,:] ) , 0 ) 
		peaks[i,:] = p 
		curr_sam = curr_sam + block_samples
	
	peaks = numpy.sort( peaks , 0 )
	rms = numpy.sort( rms , 0 )
	
	n_blk = round( seg_cnt * cut_best_bins ) 
	if n_blk == 0:
		n_blk = 1
	
	r = arange(seg_cnt-n_blk,seg_cnt) 
	
	rms_sum = numpy.sum( rms[r,:]**2 , 0 ) 
	
	ch_dr14 = -20*numpy.log10( numpy.sqrt( rms_sum / n_blk ) * 1/peaks[seg_cnt-2,:] )
	
	err_i = (rms_sum < 1/(2**24))
	ch_dr14[err_i] = 0 ;
	
	dr14 = round( numpy.mean( ch_dr_14 ) )
	
	dB_peak = decibel_u( max( peaks ) , 1 )
	
	y_rms = u_rms( Y ) 
	dB_rms = decible_u( numpy.sum( y_rms ) , 1 ) 
	
	return (dr14,dB_peak,dB_rms)
	
