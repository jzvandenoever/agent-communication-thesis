:- dynamic(state/1).
:- dynamic(in/1).
:- dynamic(at/1).
:- dynamic(visited/1).
:- dynamic(zone/5).
:- dynamic(block/3).
:- dynamic(atBlock/1).
:- dynamic(holding/1).
:- dynamic(holding/2).
:- dynamic(agent/1).
:- dynamic(sequence/1).
:- dynamic(seqDone/1).
:- dynamic(sequenceIndex/1).
:- dynamic(send/2).
:- dynamic(ahead/1).

% LookAhead agent related knowledge
agentCount(N) :- aggregate_all(count, agent(_), N).
interestingColours(CList) :- seqDone(Done), sequence(Seq), length(Done, From), agentCount(N), 
	To is From+N, findall(E, (between(From, To, I), nth0(I, Seq, E)), CList).
% No need for anything special.
wantColour(ColourID) :- not(holding(BlockID)), interestingColours(Colours), 
	member(ColourID, Colours), countOccurence(Colours, ColourID, N), 
	aggregate_all(count, (holding(_, ABlock), block(ABlock, ColourID, _)), M), M=<N.
% If we are holding a colour we need to add 1 to the count.
wantColour(ColourID) :- holding(BlockID), block(BlockID, ColorID, _), interestingColours(Colours), 
	member(ColourID, Colours), countOccurence(Colours, ColourID, N), 
	aggregate_all(count, (holding(_, ABlock), block(ABlock, ColourID, _)), M), Z is M+1, Z=<N.
% Also see what we want if we are holding something we don't want.
wantColour(ColourID) :- interestingColours(Colours), member(ColourID, Colours), 
	holding(BlockID), not(block(BlockID, ColorID, _)), countOccurence(Colours, ColourID, N), 
	aggregate_all(count, (holding(_, ABlock), block(ABlock, ColourID, _)), M), M=<N.

holdingWantBlock :- holding(BlockID),block(BlockID, ColorID, _), wantColour(ColorID).
countOccurence([],X,0).
countOccurence([X|T],X,Y):- countOccurence(T,X,Z), Y is 1+Z.
countOccurence([X1|T],X,Z):- X1\=X,countOccurence(T,X,Z).

% A room is a place with exactly one neighbour, i.e., there is only one way to get 
% to and from that place.
room(PlaceID) :- zone(_,PlaceID,_,_,Neighbours), length(Neighbours,1).
dropZone('DropZone').

% Block information.
holdingNextBlock :- holding(BlockID),block(BlockID, ColorID, Place), nextNeededColor(ColorID).
nextNeededColor(ColorID) :- sequence(Seq), seqDone(SDone), append(SDone, [ColorID|_], Seq). 
finished :- sequence(Seq), seqDone(Seq).