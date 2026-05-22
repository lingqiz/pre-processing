# Rearing

## Frame-level

| Processing                | True class      | Rearing predicted   | Not predicted | None predicted     |
|---------------------------|-------------------|---------------------|---------------|--------------------|
| Raw scores                | Rearing important | 218,136 (94.2%)     | 0 (0.0%)      | 13,493 (5.8%)      |
| Raw scores                | None important    | 5,386 (10.7%)       | 0 (0.0%)      | 44,806 (89.3%)     |
| Post-processed / filtered | Rearing important | 216,294 (93.4%)     | 0 (0.0%)      | 15,335 (6.6%)      |
| Post-processed / filtered | None important    | 3,774 (7.5%)        | 0 (0.0%)      | 46,418 (92.5%)     |

## Bout-level threshold sweep

| Threshold | Raw recall, rearing | Raw recall, negative | Raw accuracy | Filtered recall, rearing | Filtered recall, negative | Filtered accuracy |
|-----------|---------------------|----------------------|--------------|--------------------------|---------------------------|-------------------|
| 0.50      | 89.1%               | 91.5%                | 89.8%        | 82.0%                    | 93.5%                     | 85.4%             |
| 0.60      | 86.3%               | 89.9%                | 87.4%        | 80.5%                    | 93.0%                     | 84.3%             |
| 0.70      | 82.9%               | 88.3%                | 84.5%        | 78.7%                    | 92.2%                     | 82.7%             |
| 0.75      | 80.6%               | 86.4%                | 82.3%        | 77.3%                    | 91.9%                     | 81.7%             |
| 0.80      | 78.3%               | 83.8%                | 79.9%        | 76.1%                    | 91.4%                     | 80.7%             |
| 0.90      | 69.7%               | 77.6%                | 72.1%        | 71.1%                    | 88.9%                     | 76.5%             |

# Grooming

## Frame-level

| Processing                | True class       | Grooming predicted | Not predicted | None predicted     |
|---------------------------|--------------------|--------------------|---------------|--------------------|
| Raw scores                | Grooming important | 133,469 (84.4%)    | 0 (0.0%)      | 24,664 (15.6%)     |
| Raw scores                | None important     | 13,957 (9.7%)      | 0 (0.0%)      | 129,880 (90.3%)    |
| Post-processed / filtered | Grooming important | 130,320 (82.4%)    | 0 (0.0%)      | 27,813 (17.6%)     |
| Post-processed / filtered | None important     | 6,481 (4.5%)       | 0 (0.0%)      | 137,356 (95.5%)    |

## Bout-level threshold sweep

| Threshold | Raw recall, grooming | Raw recall, negative | Raw accuracy | Filtered recall, grooming | Filtered recall, negative | Filtered accuracy |
|-----------|----------------------|----------------------|--------------|---------------------------|---------------------------|-------------------|
| 0.50      | 88.8%                | 94.9%                | 93.5%        | 85.4%                     | 97.9%                     | 95.1%             |
| 0.60      | 86.1%                | 92.6%                | 91.2%        | 83.7%                     | 97.6%                     | 94.5%             |
| 0.70      | 83.3%                | 91.0%                | 89.3%        | 81.3%                     | 97.0%                     | 93.5%             |
| 0.75      | 82.3%                | 89.9%                | 88.2%        | 79.6%                     | 96.8%                     | 93.0%             |
| 0.80      | 79.9%                | 88.8%                | 86.8%        | 76.9%                     | 96.6%                     | 92.2%             |
| 0.90      | 72.8%                | 85.3%                | 82.5%        | 73.1%                     | 96.6%                     | 91.4%             |
