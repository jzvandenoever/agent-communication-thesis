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
:- dynamic(sequenceIndex/1).
:- dynamic(ahead/1).
:- dynamic(grabbing/1).
:- dynamic(grabbing/2).
:- dynamic(canGrab/2).
:- dynamic(delivered/1).

% LookAhead agent related knowledge
% Returns the amount of agents that we received a message of. This is the agents that we know of.
% By not making it static it easily adapts to differing team sizes.
agentCount(N) :- findall(Player, player(Player), Players), length(Players, N).

% A room is a place with exactly one neighbour, i.e., there is only one way to get 
% to and from that place.
room(PlaceID) :- zone(_,PlaceID,_,_,Neighbours), length(Neighbours,1).
% Predicate used to provide the dropzone location for goals and actions.
dropZone('DropZone').

% Block information.
% Gives a list of the first X blocks to be delivered in order. If X is larger than the amount of blocks
% to be delivered it just returns all blocks that still need to be delivered.
nextXColoursInSeq(Colors, X, Seq) :- sequence(SDone), append(SDone, Remainder, Seq),
	length(Colors, X), append(Colors, _, Remainder).
nextXColoursInSeq(Remainder, X, Seq) :- sequence(SDone), append(SDone, Remainder, Seq),
	length(Remainder, Y), Y<X.
% Since we often just need the colour to deliver now here's a shortcut for that.
nextColorInSeq(ColorID, Seq) :- nextXColoursInSeq([ColorID], 1, Seq).