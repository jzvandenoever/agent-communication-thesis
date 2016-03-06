% After specific runtime period messages fail.
% messageFailed :- get_time(CurrentTime), startTime(StartTime), RunTime is CurrentTime - StartTime, RunTime > 25.

% Every message has a given chance of failing. The float given is the failure rate.
% The open interval has a negligable influence on the resulting chance. (Crap ran a test with a 95% failure rate. (R>0.05)
% messageFailed :- random(R), R<0.05.
% Same as above but with a ten percent of failure.
% messageFailed :- random(R), R<0.10.
% Same as above but with a twentyfive percent of failure.
% messageFailed :- random(R), R<0.25.
% Same as above but with a fifty percent of failure.
messageFailed :- random(R), R<0.5.