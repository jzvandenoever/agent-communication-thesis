:- dynamic(state/1).
:- dynamic(in/1).
:- dynamic(at/1).
:- dynamic(visited/1).
:- dynamic(zone/5).
:- dynamic(block/3).
:- dynamic(atBlock/1).
:- dynamic(holding/1).
:- dynamic(sequence/1).
:- dynamic(seqDone/1).
:- dynamic(sequenceIndex/1).
:- dynamic(send/2).
:- dynamic(ahead/1).


% A room is a place with exactly one neighbour, i.e., there is only one way to get 
% to and from that place.
room(PlaceID) :- zone(_,PlaceID,_,_,Neighbours), length(Neighbours,1).
dropZone('DropZone').

% Block information.
holdingNextBlock :- holding(BlockID),block(BlockID, ColorID, Place), nextNeededColor(ColorID).
holdingNextBlock(N) :- holding(BlockID),block(BlockID, ColorID, Place), nextNeededColor(ColorID, N).
holdingNeededBlock(N) :- holding(BlockID), block(BlockID, ColorID, Place), seqDone(SDone), length(SDone, Len), 
	SLen is Len+1, between(SLen, N, M), nextNeededColor(ColorId, M).
nextNeededColor(ColorID) :- sequence(Seq), seqDone(SDone), append(SDone, [ColorID|_], Seq).
nextNeededColor(ColorID, N) :- sequence(Seq), seqDone(SDone), length(SDone, Len), M is Len + N, 
	nth1(M, Seq, ColorID).
finished :- sequence(Seq), seqDone(Seq).