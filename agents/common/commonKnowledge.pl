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
:- dynamic(delivered/1).
:- dynamic(delivering/2).
:- dynamic(lookahead/0).
:- dynamic(getPermission/0).
:- dynamic(deliverPermission/1).
:- dynamic(doDeliver/2).
:- dynamic(doNotDeliver/2).
:- dynamic(goingToBlock/0).

% LookAhead agent related knowledge
% Returns the amount of agents that we received a message of. This is the agents that we know of.
% By not making it static it easily adapts to differing team sizes. Do remember to count yourself however.
agentCount(N) :- not(lookahead), N = 1.
agentCount(N) :- lookahead, findall(Player, player(Player), Players), length(Players, M), N is M + 1.

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
% In case the sequence is done we need to return that there are no blocks needed and not just fail.
nextXColoursInSeq([], X, Seq) :- sequence(Seq).
% Since we often just need the colour to deliver now here's a shortcut for that.
nextColorInSeq(ColorID, Seq) :- nextXColoursInSeq([ColorID], 1, Seq).

% Get the difference between two lists like the subtract/3 predicate however duplicates are removed one to
% one. E.g. single_subtract([1,2,2,3,4],[2,4],Result). -> Result == [1,2,3]
single_subtract([],_, []).
single_subtract(Result,[], Result).
single_subtract([X|FullList], Subtracting, Result) :- member(X, Subtracting), 
	select(X, Subtracting, ReducedS), single_subtract(FullList, ReducedS, Result).
single_subtract([X|FullList], Subtracting, [X|Result]) :- not(member(X, Subtracting)), 
	single_subtract(FullList, Subtracting, Result).