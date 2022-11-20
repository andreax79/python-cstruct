/* https://www.gnu.org/software/libc/manual/html_mono/libc.html#Simple-Directory-Lister */

#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>

int main (void) {
    DIR *dp;
    struct dirent *ep;

    dp = opendir(".");
    if (dp != NULL) {
        while (ep = readdir (dp)) {
            puts(ep->d_name);
        }
        closedir(dp);
    } else {
        perror("Couldn't open the directory");
    }

    return 0;
}
