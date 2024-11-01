#!/bin/bash

jq '
  map(
    if (.tei == null) then
      . + {tei: "<persName ref=\"\(.name)\">\(.name)</persName>"}
    else
      .
    end
  )
' persons.json > persons_updated.json
