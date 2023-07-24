(defun to-org (dstfile)
  (org-mode)  

  (setq org-confirm-babel-evaluate nil)  
  (require 'ob-python)
  (org-babel-execute-buffer)  
  (write-region (point-min) (point-max) dstfile)
  )

(defun to-markdown (dstfile)
  (org-mode)  
  (require 'ox-gfm)    
  (org-gfm-export-as-markdown)
  (write-region (point-min) (point-max) dstfile))


(defun to-txt ( dstfile)
  (org-mode)  
  (org-ascii-export-as-ascii   )
  (write-region (point-min) (point-max) dstfile))

