/*
 * os9.h - System call definitions
 *
 * $Id: os9.h,v 1.3 2005/08/13 15:07:11 boisy Exp $
 *
 * (C) 2005 The C^3 Compiler Project
 * http://www.nitros9.org/c3/
 *
 * Notes:
 *
 * Edt/Rev  YYYY/MM/DD  Modified by
 * Comment
 * ------------------------------------------------------------------
 *          2005/08/12  Boisy G. Pitre
 * Brought in from Carl Kreider's CLIB package.
 */

#ifndef _OS9_H
#define _OS9_H
#include <os9abi.h>

struct registers
{
	char            rg_cc,
	                rg_a,
	                rg_b,
	                rg_dp;
	unsigned        rg_x,
	                rg_y,
	                rg_u;
};

#define F_LINK F$Link
#define F_LOAD F$Load
#define F_UNLINK F$UnLink
#define F_FORK F$Fork
#define F_WAIT F$Wait
#define F_CHAIN F$Chain
#define F_EXIT F$Exit
#define F_MEM F$Mem
#define F_SEND F$Send
#define F_ICPT F$Icpt
#define F_SLEEP F$Sleep
#define F_SSPD F$SSpd
#define F_ID F$ID
#define F_SPRIOR F$SPrior
#define F_SSWI F$SSWI
#define F_PERR F$PErr
#define F_PRSNAM F$PrsNam
#define F_CMPNAM F$CmpNam
#define F_SCHBIT F$SchBit
#define F_ALLBIT F$AllBit
#define F_DELBIT F$DelBit
#define F_TIME F$Time
#define F_STIME F$STime
#define F_CRC F$CRC
#define F_GPRDSC F$GPrDsc
#define F_GBLKMP F$GBlkMp
#define F_GMODDR F$GModDr
#define F_CPYMEM F$CpyMem
#define F_SUSER F$SUser
#define F_UNLOAD F$UnLoad
#define F_SRQMEM    0x28	/* System Memory Request */
#define F_SRTMEM    0x29	/* System Memory Return */
#define F_IRQ       0x2a	/* Enter IRQ Polling Table */
#define F_IOQU      0x2b	/* Enter I/O Queue */
#define F_APROC     0x2c	/* Enter Active Process Queue */
#define F_NPROC     0x2d	/* Start Next Process */
#define F_VMODUL    0x2e	/* Validate Module */
#define F_FIND64    0x2f	/* Find Process/Path Descriptor */
#define F_ALL64     0x30	/* Allocate Process/Path Descriptor */
#define F_RET64     0x31	/* Return Process/Path Descriptor */
#define F_SSVC      0x32	/* Service Request Table Initialization */
#define F_IODEL     0x33	/* Delete I/O Module */
#define F_SLINK     0x34	/* System Link */
#define F_BOOT      0x35	/* Bootstrap System */
#define F_BTMEM     0x36	/* Bootstrap Memory Request */
#define F_GPROCP    0x37	/* Get Process ptr */
#define F_MOVE      0x38	/* Move Data (low bound first) */
#define F_ALLRAM    0x39	/* Allocate RAM blocks */
#define F_ALLIMG    0x3a	/* Allocate Image RAM blocks */
#define F_DELIMG    0x3b	/* Deallocate Image RAM blocks */
#define F_SETIMG    0x3c	/* Set Process DAT Image */
#define F_FREELB    0x3d	/* Get Free Low Block */
#define F_FREEHB    0x3e	/* Get Free High Block */
#define F_ALLTSK    0x3f	/* Allocate Process Task number */
#define F_DELTSK    0x40	/* Deallocate Process Task number */
#define F_SETTSK    0x41	/* Set Process Task DAT registers */
#define F_RESTSK    0x42	/* Reserve Task number */
#define F_RELTSK    0x43	/* Release Task number */
#define F_DATLOG    0x44	/* Convert DAT Block/Offset to Logical */
#define F_DATTMP    0x45	/* Make temporary DAT image */
#define F_LDAXY     0x46	/* Load A [X,[Y]] */
#define F_LDAXYP    0x47	/* Load A [X+,[Y]] */
#define F_LDDDXY    0x48	/* Load D [D+X,[Y]] */
#define F_LDABX     0x49	/* Load A from 0,X in task B */
#define F_STABX     0x4a	/* Store A at 0,X in task B */
#define F_ALLPRC    0x4b	/* Allocate Process Descriptor */
#define F_DELPRC    0x4c	/* Deallocate Process Descriptor */
#define F_ELINK     0x4d	/* Link using Module Directory Entry */
#define F_FMODUL    0x4e	/* Find Module Directory Entry */
#define F_MAPBLK    0x4f	/* Map Specific Block */
#define F_CLRBLK    0x50	/* Clear Specific Block */
#define F_DELRAM    0x51	/* Deallocate RAM blocks */

#define I_ATTACH I$Attach
#define I_DETACH I$Detach
#define I_DUP I$Dup
#define I_CREATE I$Create
#define I_OPEN I$Open
#define I_MAKDIR I$MakDir
#define I_CHGDIR I$ChgDir
#define I_DELETE I$Delete
#define I_SEEK I$Seek
#define I_READ I$Read
#define I_WRITE I$Write
#define I_READLN I$ReadLn
#define I_WRITLN I$WritLn
#define I_GETSTT I$GetStt
#define I_SETSTT I$SetStt
#define I_CLOSE I$Close
#define I_DELETX I$DeletX

#define SS_OPT SS_Opt
#define SS_READY SS_Ready
#define SS_SIZE SS_Size
#define SS_RESET SS_Reset
#define SS_WTRK SS_WTrk
#define SS_POS SS_Pos
#define SS_EOF SS_EOF
#define SS_LINK SS_Link
#define SS_ULINK SS_ULink
#define SS_FEED SS_Feed
#define SS_FRZ SS_Frz
#define SS_SPT SS_SPT
#define SS_SQD SS_SQD
#define SS_DCMD SS_DCmd
#define SS_DEVNM SS_DevNm
#define SS_FD SS_FD
#define SS_TICKS SS_Ticks
#define SS_LOCK SS_Lock
#define SS_DSTAT SS_DStat
#define SS_JOY SS_Joy
#define SS_BLKRD SS_BlkRd
#define SS_BLKWR SS_BlkWr
#define SS_RETEN SS_Reten
#define SS_WFM SS_WFM
#define SS_RFM SS_RFM
#define SS_ELOG SS_ELog
#define SS_SSIG SS_SSig
#define SS_RELEA SS_Relea

#ifdef NITROS9_C3
#include <os.h>
void *modlink(const char *name, int type, int language);
void *modload(const char *name, int type, int language);
int munlink(void *module);
int getime(void *time_packet);
int setime(const void *time_packet);
int _os9(int code, registers_6809 *regs);
int lock(void);
unsigned stacksiz(void);
unsigned freemem(void);
#endif

#endif				/* _OS9_H */
