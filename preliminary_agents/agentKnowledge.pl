% A room is a place with exactly one neighbour, i.e., only way way to get to and from that place.
room(PlaceID) :- navpoint(_,PlaceID,_,_,Neighbours), length(Neighbours,1).

% Distance predicate. Based on the amount of neighbour steps.
dist(S, T, Dist) :- navpoint(_,S,_,_,Neighbours), member(T, Neighbours).
dist(S, T, Dist) :- bfs(S,T, Dist).

% Breadth First Search
bfs(S,T, Steps) :- navpoint(_,S,_,_,Edges), combine(Edges, 1, Queue), bfs(T, Steps,Queue,[S]).
bfs(T, N,[(T,N)|Queue],Searched) :- !.
bfs(T, N,[(Place, _)|Queue],Searched) :- member(Place, Searched), bfs(T, N,Queue,Searched), !.
bfs(T, N,[(Place, I)|Queue],Searched) :- navpoint(_,Place,_,_,Edges), J is I+1, subtract(Edges, Searched, NewEdges), combine(NewEdges, J, NewNodes), 
										append(Queue, NewNodes, NewQueue), bfs(T, N, NewQueue, [Place|Searched]), !.

combine([], Tuple, []).
combine([H|List], Tuple, [(H,Tuple)|Result]) :- combine(List, Tuple, Result).

% Get the currently desired color.
%getColor(Color) :- seqIndex(N), sequence(S), nth0(N, S, Color).
getColor(Color, N) :- sequence(S), nth0(N, S, Color).

someoneElseTookCareOfIt(Block) :- gettingBlock(Block,_, _).
