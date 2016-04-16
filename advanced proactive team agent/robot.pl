:- dynamic(state/1).
:- dynamic(in/1).
:- dynamic(at/1).
:- dynamic(visited/1).
:- dynamic(zone/5).
:- dynamic(block/3).
:- dynamic(atBlock/1).
:- dynamic(holding/1).
:- dynamic(heldBlock/3).
:- dynamic(sequence/1).
:- dynamic(seqDone/1).
:- dynamic(sequenceIndex/1).
:- dynamic(hiddenSequenceIndex/1).
:- dynamic(send/2).
:- dynamic(me/1).
:- dynamic(teamGoal/2).
:- dynamic(aheadIndex/1).


% A room is a place with exactly one neighbour, i.e., there is only one way to get to and from that place.
room(PlaceID) :- zone(_,PlaceID,_,_,Neighbours), length(Neighbours,1).
dropZone('DropZone').

% Block information.
holdingNextBlock :- holding(BlockID),block(BlockID, ColorID, Place), nextNeededColor(ColorID).
nextNeededColor(ColorID, At) :- sequence(Seq), nth0(At, Seq, ColorID).
nextNeededColor(ColorID) :- sequenceIndex(N), nextNeededColor(ColorID, N). 
finished :- sequence(Seq), length(Seq, N), sequenceIndex(M), M == N.