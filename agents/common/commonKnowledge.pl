:- dynamic(me/1).
:- dynamic(state/1).
:- dynamic(in/1).
:- dynamic(at/1).
:- dynamic(visited/1).
:- dynamic(zone/5).
:- dynamic(block/3).
:- dynamic(atBlock/1).
:- dynamic(holding/1).
:- dynamic(holding/2).
:- dynamic(player/1).
:- dynamic(sequence/1).
:- dynamic(seqDone/1).
:- dynamic(sequenceIndex/1).
:- dynamic(ahead/1).
:- dynamic(grabbing/1).
:- dynamic(grabbing/2).
:- dynamic(canGrab/2).

% LookAhead agent related knowledge
% Returns the amount of agents that we received a message of. This is the agents that we know of.
% By not making it static it easily adapts to differing team sizes.
agentCount(N) :- findall(Player, player(Player), Players), length(Players, N).

% The subset of the sequence from the current needed block with the next N blocks. Where N is 
% agentCount(N).
interestingColours(CList) :- stillNeededColours(List), agentCount(N), length(CList, N),
	append(CList, _, List).
stillNeededColours(CList) :- seqDone(Done), sequence(Seq), append(Done, CList, Seq).
% If we are not holding something we check what colours that are interesting are already being held.
% When one colour is found that is not already picked up or going to be picked up at the needed amount,
% it is wanted. If we are holding that colour we can check if it is wanted by providing the colour of
% that block
wantColour(ColourID) :- interestingColours(Colours), member(ColourID, Colours), 
	countOccurence(Colours, ColourID, N), 
	findall(ABlock, ((holding(_, ABlock); grabbing(_,ABlock)), block(ABlock, ColourID, _)), Blocks), 
	length(Blocks, M), M<N.
%wantColour(ColourID) :- interestingColours(Colours), member(ColourID, Colours), 
%	countOccurence(Colours, ColourID, N).

% The block being held is a block that is wanted.
holdingWantBlock :- holding(BlockID),block(BlockID, ColorID, _), wantColour(ColorID).

% Counts the amount of times X is in list.
countOccurence([],X,0).
countOccurence([X|T],X,Y):- countOccurence(T,X,Z), Y is 1+Z.
countOccurence([X1|T],X,Z):- X1\=X,countOccurence(T,X,Z).

% A room is a place with exactly one neighbour, i.e., there is only one way to get 
% to and from that place.
room(PlaceID) :- zone(_,PlaceID,_,_,Neighbours), length(Neighbours,1).
% Predicate used to provide the dropzone location for goals and actions.
dropZone('DropZone').

% Block information.
% Is the agent holding the next needed block.
holdingNextBlock :- holding(BlockID),block(BlockID, ColorID, Place), nextNeededColor(ColorID).
% What is the current colour that needs to be dropped off.
nextNeededColor(ColorID) :- sequence(Seq), seqDone(SDone), append(SDone, [ColorID|_], Seq).

% This detects if the agents has finished. 
%Is used to exit immediately once the goal is complete by any agent.
finished :- sequence(Seq), seqDone(Seq).