import { Rank } from "@/api/types";

const rankTexts: Partial<Record<Rank, string>> = {
  ace: "A",
  king: "K",
  queen: "Q",
  jack: "J",
};

export function rankText(rank: Rank) {
  return rankTexts[rank] || rank;
}
