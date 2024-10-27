
(defun gps-line ()
  "Print the current buffer line number and narrowed line number of point."
  (interactive)
  (let ((start (point-min))
	(n (line-number-at-pos))
        (total-lines (save-excursion
	               (goto-char (point-min))
		       (count-matches "\n" (point-min) (point-max)))))
    (if (= start 1)
	(message "Line %d/%d" n total-lines)
      (save-excursion
	(save-restriction
	  (widen)
	  (message "line %d/%d (narrowed from line %d)"
		   (+ n (line-number-at-pos start) -1)
		   total-lines
		   (line-number-at-pos start)))))))
