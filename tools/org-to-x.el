;; convert org to something else in a batch file.
;; emacs opened with src in current buffer, dst as
;; command line argument
(require 'ox-gfm)
(setq dstfile (elt argv 2))


(defun sc/execute ()
  (require 'ob-python)
  (message "ERRRORRR")

  ;; do the executing in fakeorg.py now
  ;;
  ;;  (org-babel-execute-buffer)
  )

(defun sc/tomd ()
  (org-gfm-export-as-markdown))

(defun sc/fnfromext (ext)
  (cdr (assoc ext
              '(("org" . sc/execute)
                ("torg" . sc/execute)
                ("md" . sc/tomd)
                ("txt" . org-ascii-export-as-ascii)
                ("html" . org-html-export-as-html)))))

(defun org-to-any1 (dstfile)
  (org-mode)
  (message "building %s" dstfile)
  (setq org-ascii-charset 'utf-8)
  (setq org-confirm-babel-evaluate nil)
  (funcall (sc/fnfromext (downcase (file-name-extension dstfile))))
  (delete-file (concat dstfile ".tmp"))
  (delete-file (concat dstfile ".md"))
  (delete-file (concat dstfile ".md.tmp"))
  (write-region (point-min) (point-max) dstfile)

  )



(defun org-to-any ()
  (org-to-any1 dstfile))
